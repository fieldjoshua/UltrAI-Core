import { useState, useEffect, useCallback } from 'react';

// Define the cache structure
interface CacheItem<T> {
  value: T;
  timestamp: number;
  expiry: number | null; // null for no expiry
}

interface CacheOptions {
  /**
   * Time to live in milliseconds. Default is 24 hours.
   * Set to null for no expiry.
   */
  ttl?: number | null;
  
  /**
   * Storage key prefix
   */
  keyPrefix?: string;
  
  /**
   * Max number of items to store in cache
   */
  maxItems?: number;
  
  /**
   * Whether to debug log cache operations
   */
  debug?: boolean;
}

/**
 * Hook for managing offline data caching
 * @param initialCache - Optional initial cache
 * @param options - Cache options
 */
export function useOfflineCache<T = any>(
  initialCache: Record<string, T> = {},
  options: CacheOptions = {}
) {
  // Default options
  const { 
    ttl = 24 * 60 * 60 * 1000, // 24 hours in milliseconds
    keyPrefix = 'ultra_cache:',
    maxItems = 1000,
    debug = false
  } = options;
  
  // Initialize the cache state
  const [cache, setCache] = useState<Record<string, CacheItem<T>>>({});
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Initialize the cache from localStorage
  useEffect(() => {
    const loadCache = () => {
      try {
        // Only load items with matching prefix
        const items: Record<string, CacheItem<T>> = {};
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i) || '';
          if (key.startsWith(keyPrefix)) {
            const rawItem = localStorage.getItem(key);
            if (rawItem) {
              try {
                const item = JSON.parse(rawItem) as CacheItem<T>;
                // Check expiry
                if (item.expiry === null || item.expiry > Date.now()) {
                  const actualKey = key.substring(keyPrefix.length);
                  items[actualKey] = item;
                } else {
                  // Expired, remove it
                  localStorage.removeItem(key);
                }
              } catch (e) {
                if (debug) console.error(`Failed to parse cache item ${key}:`, e);
                localStorage.removeItem(key);
              }
            }
          }
        }
        
        // Add initial cache items
        Object.entries(initialCache).forEach(([key, value]) => {
          const now = Date.now();
          items[key] = {
            value,
            timestamp: now,
            expiry: ttl === null ? null : now + ttl
          };
        });
        
        setCache(items);
        setIsInitialized(true);
        
        if (debug) {
          console.log(`Loaded ${Object.keys(items).length} items from cache`);
        }
      } catch (e) {
        console.error('Error loading cache from localStorage:', e);
        setCache({});
        setIsInitialized(true);
      }
    };
    
    loadCache();
  }, [keyPrefix, ttl, debug]);
  
  // Save the cache to localStorage whenever it changes
  useEffect(() => {
    if (!isInitialized) return;
    
    try {
      // Clear existing items first
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i) || '';
        if (key.startsWith(keyPrefix)) {
          localStorage.removeItem(key);
        }
      }
      
      // Save current cache items
      Object.entries(cache).forEach(([key, item]) => {
        localStorage.setItem(`${keyPrefix}${key}`, JSON.stringify(item));
      });
      
      if (debug) {
        console.log(`Saved ${Object.keys(cache).length} items to cache`);
      }
    } catch (e) {
      console.error('Error saving cache to localStorage:', e);
    }
  }, [cache, isInitialized, keyPrefix, debug]);
  
  // Clean up expired items periodically
  useEffect(() => {
    if (!isInitialized) return;
    
    const cleanup = () => {
      setCache(currentCache => {
        const now = Date.now();
        const updatedCache: Record<string, CacheItem<T>> = {};
        let expiredCount = 0;
        
        Object.entries(currentCache).forEach(([key, item]) => {
          if (item.expiry === null || item.expiry > now) {
            updatedCache[key] = item;
          } else {
            expiredCount++;
          }
        });
        
        if (debug && expiredCount > 0) {
          console.log(`Cleaned up ${expiredCount} expired items from cache`);
        }
        
        return updatedCache;
      });
    };
    
    // Run cleanup immediately, then at regular intervals
    cleanup();
    
    // Set interval for every 5 minutes
    const interval = setInterval(cleanup, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [isInitialized, debug]);
  
  // Function to get a value from the cache
  const get = useCallback((key: string): T | undefined => {
    const item = cache[key];
    
    if (!item) {
      if (debug) console.log(`Cache miss for ${key}`);
      return undefined;
    }
    
    // Check expiry
    if (item.expiry !== null && item.expiry <= Date.now()) {
      if (debug) console.log(`Cache item ${key} has expired`);
      
      // Remove the expired item
      setCache(currentCache => {
        const { [key]: _, ...rest } = currentCache;
        return rest;
      });
      
      return undefined;
    }
    
    if (debug) console.log(`Cache hit for ${key}`);
    return item.value;
  }, [cache, debug]);
  
  // Function to set a value in the cache
  const set = useCallback((key: string, value: T, itemTtl?: number | null): void => {
    const now = Date.now();
    const effectiveTtl = itemTtl !== undefined ? itemTtl : ttl;
    
    setCache(currentCache => {
      // Check if we have too many items
      if (Object.keys(currentCache).length >= maxItems && !(key in currentCache)) {
        // Evict the oldest item
        const cacheEntries = Object.entries(currentCache);
        cacheEntries.sort((a, b) => a[1].timestamp - b[1].timestamp);
        
        if (debug && cacheEntries.length > 0) {
          console.log(`Cache at capacity, evicting oldest item: ${cacheEntries[0][0]}`);
        }
        
        const [oldestKey] = cacheEntries[0] || [null];
        
        if (oldestKey) {
          const { [oldestKey]: _, ...restCache } = currentCache;
          return {
            ...restCache,
            [key]: {
              value,
              timestamp: now,
              expiry: effectiveTtl === null ? null : now + effectiveTtl
            }
          };
        }
      }
      
      // Otherwise just add/update the item
      return {
        ...currentCache,
        [key]: {
          value,
          timestamp: now,
          expiry: effectiveTtl === null ? null : now + effectiveTtl
        }
      };
    });
    
    if (debug) console.log(`Set cache item ${key}`);
  }, [ttl, maxItems, debug]);
  
  // Function to remove a value from the cache
  const remove = useCallback((key: string): void => {
    setCache(currentCache => {
      const { [key]: _, ...rest } = currentCache;
      return rest;
    });
    
    if (debug) console.log(`Removed cache item ${key}`);
  }, [debug]);
  
  // Function to clear the entire cache
  const clear = useCallback((): void => {
    setCache({});
    
    // Also clear localStorage items with the prefix
    try {
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i) || '';
        if (key.startsWith(keyPrefix)) {
          localStorage.removeItem(key);
        }
      }
    } catch (e) {
      console.error('Error clearing cache from localStorage:', e);
    }
    
    if (debug) console.log('Cleared entire cache');
  }, [keyPrefix, debug]);
  
  // Function to check if a key exists and is not expired
  const has = useCallback((key: string): boolean => {
    const item = cache[key];
    if (!item) return false;
    
    // Check expiry
    return item.expiry === null || item.expiry > Date.now();
  }, [cache]);
  
  // Functions to get all keys, values, or entries
  const keys = useCallback((): string[] => {
    return Object.keys(cache);
  }, [cache]);
  
  const values = useCallback((): T[] => {
    return Object.values(cache).map(item => item.value);
  }, [cache]);
  
  const entries = useCallback((): [string, T][] => {
    return Object.entries(cache).map(([key, item]) => [key, item.value]);
  }, [cache]);
  
  // Get the current size of the cache
  const size = Object.keys(cache).length;
  
  return {
    get,
    set,
    remove,
    clear,
    has,
    keys,
    values,
    entries,
    size,
    isInitialized
  };
}

export default useOfflineCache;