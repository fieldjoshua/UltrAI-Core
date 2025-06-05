# Performance Optimization Guidelines

## Core Optimizations (Always Apply)

### 1. Multiprocessing for Independent Tasks

```python
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor

# Use for CPU-bound parallel tasks
with Pool() as p:
    results = p.map(cpu_intensive_function, data)
```

### 2. Threading for I/O Operations

```python
from concurrent.futures import ThreadPoolExecutor

# Use for I/O-bound operations (API calls, file operations)
with ThreadPoolExecutor() as executor:
    results = list(executor.map(io_operation, items))
```

### 3. Caching for Repeated Calculations

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param):
    return complex_calculation(param)
```

## Conditional Optimizations (Context-Specific)

### NumPy (for numerical operations on large datasets)

**When to use:**

- Arrays with >1000 elements
- Matrix operations
- Statistical calculations

**When NOT to use:**

- Small datasets (<100 elements)
- General Python operations
- String manipulation

### Numba (for numerical loops)

**When to use:**

- Loops with >10,000 iterations
- Pure numerical calculations
- Scientific computing

**When NOT to use:**

- Small loops
- Python objects (dict, list operations)
- First-time execution (compilation overhead)

## Decision Matrix

| Optimization    | Use When              | Don't Use When            | Speedup  |
| --------------- | --------------------- | ------------------------- | -------- |
| Multiprocessing | Independent CPU tasks | Small tasks, shared state | 2-8x     |
| Threading       | I/O operations        | CPU-bound tasks           | 2-10x    |
| Caching         | Repeated calculations | Unique inputs             | 10-1000x |
| NumPy           | Large arrays (>1000)  | Small data                | 10-100x  |
| Numba           | Heavy loops (>10k)    | Small operations          | 10-100x  |

## Implementation Strategy

1. **Profile First**: Use cProfile to identify bottlenecks
2. **Apply Incrementally**: Start with multiprocessing/threading
3. **Measure Impact**: Benchmark before and after
4. **Context Matters**: Choose based on data size and operation type
