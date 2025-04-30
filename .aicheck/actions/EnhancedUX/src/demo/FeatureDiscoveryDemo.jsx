import React, { useState, useEffect } from 'react';
import {
  createExperienceTracker,
  createAchievementSystem,
  ProgressiveDisclosure,
  AchievementNotification,
} from '../feature_discovery';
import GuidedTour from '../components/GuidedTour';
import ContextualHelp from '../components/ContextualHelp';
import './FeatureDiscoveryDemo.css';

/**
 * Feature Discovery Demo
 *
 * Demonstrates all the components of the feature discovery system:
 * - Progressive feature disclosure
 * - Achievement system
 * - Guided tour
 * - Contextual help
 */
const FeatureDiscoveryDemo = () => {
  // Set up state
  const [experienceLevel, setExperienceLevel] = useState('beginner');
  const [discoveryMode, setDiscoveryMode] = useState(false);
  const [experiencePoints, setExperiencePoints] = useState(0);
  const [unlockedAchievements, setUnlockedAchievements] = useState([]);
  const [currentAchievement, setCurrentAchievement] = useState(null);
  const [isTourOpen, setIsTourOpen] = useState(false);

  // Initialize experience tracker and achievement system
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

    // Subscribe to achievement unlocks
    achievements.subscribe((event) => {
      if (event.type === 'ACHIEVEMENT_UNLOCKED') {
        setCurrentAchievement(event.achievement);
      }
    });

    // Subscribe to experience changes
    tracker.subscribe((event) => {
      if (event.type === 'ACTIVITY_RECORDED') {
        setExperiencePoints(event.newScore);
        setExperienceLevel(event.currentLevel);
      }
    });

    return { tracker, achievements };
  });

  // Simulate user actions to gain experience
  const performAction = (actionType, details = {}) => {
    const result = systems.tracker.recordActivity(actionType, details);

    // Check if certain actions trigger achievement unlocks
    if (
      actionType === 'FEATURE_USED' &&
      details.featureId === 'dataVisualization'
    ) {
      systems.achievements.unlockAchievement('visualization_master');
    }

    return result;
  };

  // Load custom achievements
  useEffect(() => {
    systems.achievements.registerAchievements([
      {
        id: 'first_analysis',
        title: 'DATA PIONEER',
        description: 'Complete your first data analysis',
        tier: 'BRONZE',
        category: 'discovery',
        icon: '📊',
      },
      {
        id: 'visualization_master',
        title: 'VISUAL INNOVATOR',
        description: 'Master the data visualization tools',
        tier: 'SILVER',
        category: 'mastery',
        icon: '📈',
      },
      {
        id: 'neural_network',
        title: 'NEURAL NETWORK ADEPT',
        description: 'Train your first neural network model',
        tier: 'GOLD',
        category: 'mastery',
        icon: '🧠',
      },
    ]);

    // Get unlocked achievements
    setUnlockedAchievements(systems.achievements.getUnlockedAchievements());
  }, [systems.achievements]);

  // Handle feature discovery
  const handleFeatureDiscovered = (featureId, requiredLevel) => {
    console.log(
      `Feature discovered: ${featureId}, required level: ${requiredLevel}`
    );
    performAction('FEATURE_DISCOVERED', { featureId, requiredLevel });
  };

  // Clear achievement notification
  const handleAchievementClose = () => {
    setCurrentAchievement(null);
  };

  // Tour steps for guided tour
  const tourSteps = [
    {
      element: '#basic-features',
      title: 'BASIC FEATURES',
      content:
        'Start with these fundamental tools to get familiar with the system.',
      position: 'bottom',
    },
    {
      element: '#intermediate-features',
      title: 'INTERMEDIATE FEATURES',
      content:
        'As you gain experience, these more advanced tools will become available.',
      position: 'right',
    },
    {
      element: '#advanced-features',
      title: 'ADVANCED FEATURES',
      content: 'Master the system to unlock these powerful capabilities.',
      position: 'top',
    },
    {
      element: '#help-section',
      title: 'CONTEXTUAL HELP',
      content:
        'Help is always available. Hover over any element with a blue glow for more information.',
      position: 'left',
    },
  ];

  return (
    <div className="feature-discovery-demo">
      <header className="demo-header">
        <h1>
          ULTRA<span className="accent">AI</span> INTERFACE
        </h1>
        <div className="experience-display">
          <div className="experience-level">
            LEVEL:{' '}
            <span className={`level-${experienceLevel}`}>
              {experienceLevel.toUpperCase()}
            </span>
          </div>
          <div className="experience-bar">
            <div
              className="experience-progress"
              style={{
                width: `${systems.tracker.getProgressToNextLevel()}%`,
              }}
            />
          </div>
          <div className="experience-points">XP: {experiencePoints}</div>
        </div>
      </header>

      <main className="demo-content">
        <section className="demo-sidebar">
          <div className="demo-controls">
            <h2>DEMO CONTROLS</h2>
            <div className="control-item">
              <label>
                <input
                  type="checkbox"
                  checked={discoveryMode}
                  onChange={() => setDiscoveryMode(!discoveryMode)}
                />
                Discovery Mode
              </label>
            </div>
            <div className="control-buttons">
              <button
                onClick={() =>
                  performAction('FEATURE_USED', { featureId: 'basicAnalysis' })
                }
              >
                Perform Basic Analysis (+5 XP)
              </button>
              <button
                onClick={() =>
                  performAction('COMPLEX_TASK', { taskId: 'dataIntegration' })
                }
              >
                Complete Complex Task (+10 XP)
              </button>
              <button
                onClick={() =>
                  systems.achievements.unlockAchievement('first_analysis')
                }
              >
                Unlock Achievement
              </button>
              <button onClick={() => setIsTourOpen(true)}>
                Start Guided Tour
              </button>
            </div>
          </div>

          <div className="unlocked-achievements">
            <h2>ACHIEVEMENTS</h2>
            {unlockedAchievements.length === 0 ? (
              <p className="no-achievements">No achievements unlocked yet</p>
            ) : (
              <ul className="achievement-list">
                {unlockedAchievements.map((achievement) => (
                  <li
                    key={achievement.id}
                    className={`achievement-item tier-${achievement.tier.toLowerCase()}`}
                  >
                    <span className="achievement-icon">{achievement.icon}</span>
                    <div className="achievement-info">
                      <h4>{achievement.title}</h4>
                      <p>{achievement.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <section className="demo-main-content">
          <div id="help-section">
            <h2>FEATURE DISCOVERY SYSTEM</h2>
            <p>
              This demo showcases how features are progressively revealed as
              users gain experience.
              <span id="help-tooltip" className="has-tooltip">
                {' '}
                Need help?
              </span>
              <ContextualHelp
                targetId="#help-tooltip"
                content="The Feature Discovery System helps users learn about features at their own pace."
                title="HELP SYSTEM"
                type="tooltip"
                trigger="hover"
              />
            </p>
          </div>

          <div id="features-container" className="features-container">
            <div id="basic-features" className="feature-section">
              <h3>BASIC FEATURES</h3>
              <ProgressiveDisclosure
                requiredLevel="beginner"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="dataAnalysis"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Data Analysis</h4>
                  <p>Analyze your data with simple visualization tools.</p>
                  <span id="analysis-help" className="has-tooltip">
                    ℹ️
                  </span>
                  <ContextualHelp
                    targetId="#analysis-help"
                    content="Start with basic analysis to understand your data structure."
                    title="DATA ANALYSIS"
                    type="tooltip"
                  />
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>

              <ProgressiveDisclosure
                requiredLevel="beginner"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="simpleReports"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Simple Reports</h4>
                  <p>Generate basic reports from your analysis results.</p>
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>
            </div>

            <div id="intermediate-features" className="feature-section">
              <h3>INTERMEDIATE FEATURES</h3>
              <ProgressiveDisclosure
                requiredLevel="intermediate"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="dataVisualization"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Advanced Visualization</h4>
                  <p>Create interactive charts and complex visualizations.</p>
                  <span id="viz-popover" className="has-tooltip">
                    ⚙️
                  </span>
                  <ContextualHelp
                    targetId="#viz-popover"
                    content="Visualizations help identify patterns and trends in your data that might not be obvious from tables alone."
                    title="VISUALIZATION TOOLS"
                    type="popover"
                    trigger="click"
                  />
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>

              <ProgressiveDisclosure
                requiredLevel="intermediate"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="dataIntegration"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Data Integration</h4>
                  <p>Connect to external data sources for richer analysis.</p>
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>
            </div>

            <div id="advanced-features" className="feature-section">
              <h3>ADVANCED FEATURES</h3>
              <ProgressiveDisclosure
                requiredLevel="advanced"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="neuralNetworks"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Neural Networks</h4>
                  <p>Train and deploy custom neural networks for your data.</p>
                  <span id="neural-hint" className="has-tooltip">
                    🔥
                  </span>
                  <ContextualHelp
                    targetId="#neural-hint"
                    content="Neural networks can identify complex patterns in your data automatically."
                    title="NEW FEATURE"
                    type="hint"
                    trigger="click"
                  />
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>

              <ProgressiveDisclosure
                requiredLevel="advanced"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="predictionModels"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card">
                  <h4>Prediction Models</h4>
                  <p>
                    Create models that forecast future trends based on your
                    data.
                  </p>
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>
            </div>

            <div className="feature-section">
              <h3>EXPERT FEATURES</h3>
              <ProgressiveDisclosure
                requiredLevel="expert"
                currentLevel={experienceLevel}
                discoveryMode={discoveryMode}
                identifier="customAlgorithms"
                onDiscovery={handleFeatureDiscovered}
              >
                <div className="feature-card special">
                  <h4>Custom Algorithms</h4>
                  <p>
                    Define your own algorithms for specialized data processing.
                  </p>
                  <button>Use Feature</button>
                </div>
              </ProgressiveDisclosure>
            </div>
          </div>
        </section>
      </main>

      {/* Guided Tour */}
      <GuidedTour
        steps={tourSteps}
        isOpen={isTourOpen}
        onComplete={() => {
          setIsTourOpen(false);
          performAction('GUIDE_COMPLETED', { tourId: 'featureDiscovery' });
        }}
        onSkip={() => setIsTourOpen(false)}
      />

      {/* Achievement Notification */}
      {currentAchievement && (
        <AchievementNotification
          achievement={currentAchievement}
          onClose={handleAchievementClose}
          autoHide={true}
          duration={5000}
        />
      )}
    </div>
  );
};

export default FeatureDiscoveryDemo;
