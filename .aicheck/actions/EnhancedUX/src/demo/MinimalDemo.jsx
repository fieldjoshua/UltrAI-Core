import React, { useState, useEffect } from 'react';
import {
  createExperienceTracker,
  createAchievementSystem,
  ProgressiveDisclosure,
} from '../feature_discovery';
import ContextualHelp from '../components/ContextualHelp';

/**
 * Minimal Feature Discovery Demo
 *
 * Shows the core functionality with minimal styling:
 * - Progressive feature disclosure based on experience level
 * - Experience tracking and level progression
 * - Feature discovery notifications
 * - Basic contextual help
 */
const MinimalDemo = () => {
  const [experienceLevel, setExperienceLevel] = useState('beginner');
  const [experiencePoints, setExperiencePoints] = useState(0);
  const [discoveredFeatures, setDiscoveredFeatures] = useState([]);
  const [notification, setNotification] = useState(null);

  // Initialize systems
  const [systems] = useState(() => {
    const tracker = createExperienceTracker({
      initialLevel: 'beginner',
      thresholds: {
        intermediate: 25,
        advanced: 75,
        expert: 150,
      },
    });

    const achievements = createAchievementSystem({}, tracker);

    // Track experience changes
    tracker.subscribe((event) => {
      if (event.type === 'ACTIVITY_RECORDED') {
        setExperiencePoints(event.newScore);
        setExperienceLevel(event.currentLevel);
      }

      if (event.type === 'FEATURE_DISCOVERED') {
        setDiscoveredFeatures((prev) => [...prev, event.featureId]);
        setNotification(`New feature discovered: ${event.featureId}`);

        // Clear notification after 3 seconds
        setTimeout(() => setNotification(null), 3000);
      }
    });

    return { tracker, achievements };
  });

  // Record user actions
  const performAction = (actionType, details = {}) => {
    systems.tracker.recordActivity(actionType, details);
  };

  // Handle feature discovery
  const handleFeatureDiscovered = (featureId, requiredLevel) => {
    systems.tracker.discoverFeature(featureId, requiredLevel);
  };

  // Simple notification component
  const Notification = ({ message }) => {
    if (!message) return null;

    return (
      <div
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          background: '#333',
          color: 'white',
          padding: '10px 15px',
          borderRadius: '4px',
          zIndex: 1000,
        }}
      >
        {message}
      </div>
    );
  };

  // Progress bar component
  const ProgressBar = ({ value, max }) => {
    const percentage = Math.min(100, Math.round((value / max) * 100)) || 0;

    return (
      <div
        style={{
          width: '100%',
          height: '10px',
          background: '#eee',
          borderRadius: '5px',
          margin: '10px 0',
        }}
      >
        <div
          style={{
            width: `${percentage}%`,
            height: '100%',
            background: '#0088ff',
            borderRadius: '5px',
            transition: 'width 0.3s ease',
          }}
        />
      </div>
    );
  };

  return (
    <div
      style={{
        fontFamily: 'sans-serif',
        maxWidth: '800px',
        margin: '0 auto',
        padding: '20px',
      }}
    >
      <h1>Feature Discovery Demo</h1>

      {/* User level information */}
      <div
        style={{
          padding: '15px',
          background: '#f5f5f5',
          borderRadius: '5px',
          marginBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span>
            Experience Level: <strong>{experienceLevel}</strong>
          </span>
          <span>XP: {experiencePoints}</span>
        </div>

        <ProgressBar
          value={experiencePoints}
          max={systems.tracker.getNextLevel()?.threshold || 200}
        />

        <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
          <button
            onClick={() =>
              performAction('FEATURE_USED', { featureId: 'basic' })
            }
          >
            Basic Action (+5 XP)
          </button>
          <button onClick={() => performAction('COMPLEX_TASK')}>
            Complex Action (+10 XP)
          </button>
        </div>
      </div>

      {/* Feature sections */}
      <div
        style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}
      >
        {/* Basic features */}
        <div
          style={{
            border: '1px solid #ddd',
            padding: '15px',
            borderRadius: '5px',
          }}
        >
          <h2>Basic Features</h2>

          <ProgressiveDisclosure
            requiredLevel="beginner"
            currentLevel={experienceLevel}
            identifier="dataAnalysis"
            onDiscovery={handleFeatureDiscovered}
          >
            <div
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '10px',
              }}
            >
              <h3 style={{ margin: '0 0 10px 0' }}>Data Analysis</h3>
              <p>Analyze your data with simple tools.</p>
              <button>Use Feature</button>
              <span
                id="help-icon"
                style={{ marginLeft: '10px', cursor: 'help' }}
              >
                ℹ️
              </span>
              <ContextualHelp
                targetId="#help-icon"
                content="Basic data analysis tools for beginners."
                type="tooltip"
              />
            </div>
          </ProgressiveDisclosure>
        </div>

        {/* Intermediate features */}
        <div
          style={{
            border: '1px solid #ddd',
            padding: '15px',
            borderRadius: '5px',
          }}
        >
          <h2>Intermediate Features</h2>

          <ProgressiveDisclosure
            requiredLevel="intermediate"
            currentLevel={experienceLevel}
            identifier="dataVisualization"
            onDiscovery={handleFeatureDiscovered}
          >
            <div
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '10px',
              }}
            >
              <h3 style={{ margin: '0 0 10px 0' }}>Data Visualization</h3>
              <p>Create charts and visualizations.</p>
              <button>Use Feature</button>
            </div>
          </ProgressiveDisclosure>
        </div>

        {/* Advanced features */}
        <div
          style={{
            border: '1px solid #ddd',
            padding: '15px',
            borderRadius: '5px',
          }}
        >
          <h2>Advanced Features</h2>

          <ProgressiveDisclosure
            requiredLevel="advanced"
            currentLevel={experienceLevel}
            identifier="machineLearning"
            onDiscovery={handleFeatureDiscovered}
          >
            <div
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '10px',
              }}
            >
              <h3 style={{ margin: '0 0 10px 0' }}>Machine Learning</h3>
              <p>Train models on your data.</p>
              <button>Use Feature</button>
            </div>
          </ProgressiveDisclosure>
        </div>

        {/* Expert features */}
        <div
          style={{
            border: '1px solid #ddd',
            padding: '15px',
            borderRadius: '5px',
          }}
        >
          <h2>Expert Features</h2>

          <ProgressiveDisclosure
            requiredLevel="expert"
            currentLevel={experienceLevel}
            identifier="customAlgorithms"
            onDiscovery={handleFeatureDiscovered}
          >
            <div
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                marginBottom: '10px',
              }}
            >
              <h3 style={{ margin: '0 0 10px 0' }}>Custom Algorithms</h3>
              <p>Build your own algorithms.</p>
              <button>Use Feature</button>
            </div>
          </ProgressiveDisclosure>
        </div>
      </div>

      {/* Discovered features */}
      <div
        style={{
          marginTop: '20px',
          padding: '15px',
          background: '#f5f5f5',
          borderRadius: '5px',
        }}
      >
        <h2>Discovered Features</h2>
        {discoveredFeatures.length === 0 ? (
          <p>No features discovered yet.</p>
        ) : (
          <ul>
            {discoveredFeatures.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Notification */}
      <Notification message={notification} />
    </div>
  );
};

export default MinimalDemo;
