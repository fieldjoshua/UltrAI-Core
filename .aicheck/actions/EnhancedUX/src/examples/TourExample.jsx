import React, { useState } from 'react';
import GuidedTour from '../components/GuidedTour';
import '../components/GuidedTour.css';
import './TourExample.css';

const TourExample = () => {
  const [isTourOpen, setIsTourOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [tourCompleted, setTourCompleted] = useState(false);

  // Example tour steps
  const tourSteps = [
    {
      target: '#dashboard-header',
      title: 'Welcome to Ultra',
      content:
        'This guided tour will show you the key features of our cyberpunk interface. Ready to explore?',
      placement: 'bottom',
    },
    {
      target: '#analytics-panel',
      title: 'Real-time Analytics',
      content:
        'Monitor your system performance with our advanced neural network analytics engine.',
      placement: 'right',
      highlightPadding: 8,
    },
    {
      target: '#control-panel',
      title: 'Command Center',
      content:
        'Control all aspects of your system from this centralized command panel.',
      placement: 'left',
      extraContent: (
        <div className="tour-extra-info">
          <h4>Pro Tip</h4>
          <p>
            Use keyboard shortcuts (Alt+C) to quickly access the command
            console.
          </p>
        </div>
      ),
    },
    {
      target: '#notification-center',
      title: 'Notification Hub',
      content:
        'Stay updated with real-time alerts and system notifications in this centralized hub.',
      placement: 'top',
      image: 'https://placehold.co/300x150/001122/00ccff?text=Notification+Hub',
    },
    {
      target: '#user-profile',
      title: 'Your Neural Profile',
      content:
        'Customize your experience and manage your personal settings from your neural profile.',
      placement: 'bottom-end',
    },
  ];

  const handleTourComplete = () => {
    setTourCompleted(true);
    setIsTourOpen(false);
    console.log('Tour completed!');
  };

  const handleTourSkip = () => {
    setIsTourOpen(false);
    console.log('Tour skipped!');
  };

  const handleStepChange = (stepIndex) => {
    setActiveStep(stepIndex);
    console.log(`Step changed to: ${stepIndex}`);
  };

  const startTour = () => {
    setIsTourOpen(true);
    setTourCompleted(false);
    setActiveStep(0);
  };

  return (
    <div className="tour-example-container">
      <header id="dashboard-header" className="example-section">
        <h1>Ultra Dashboard</h1>
        <p>Welcome to the next generation interface</p>
      </header>

      <div className="dashboard-layout">
        <section id="analytics-panel" className="example-section">
          <h2>Analytics Engine</h2>
          <div className="mock-chart">
            <div className="chart-bar" style={{ height: '60%' }}></div>
            <div className="chart-bar" style={{ height: '80%' }}></div>
            <div className="chart-bar" style={{ height: '40%' }}></div>
            <div className="chart-bar" style={{ height: '90%' }}></div>
            <div className="chart-bar" style={{ height: '50%' }}></div>
          </div>
        </section>

        <section id="control-panel" className="example-section">
          <h2>System Controls</h2>
          <div className="control-buttons">
            <button className="cybr-btn">Initialize</button>
            <button className="cybr-btn">Configure</button>
            <button className="cybr-btn">Optimize</button>
          </div>
        </section>

        <section id="notification-center" className="example-section">
          <h2>Notifications</h2>
          <ul className="notification-list">
            <li>System update available</li>
            <li>Security scan complete</li>
            <li>New feature unlocked</li>
          </ul>
        </section>

        <section id="user-profile" className="example-section">
          <h2>Neural Profile</h2>
          <div className="profile-avatar"></div>
          <p>NetRunner_2077</p>
        </section>
      </div>

      <div className="tour-controls">
        <button
          className="start-tour-btn"
          onClick={startTour}
          disabled={isTourOpen}
        >
          {tourCompleted ? 'Restart Tour' : 'Start Guided Tour'}
        </button>
      </div>

      {/* Guided Tour Component */}
      <GuidedTour
        steps={tourSteps}
        isOpen={isTourOpen}
        onComplete={handleTourComplete}
        onSkip={handleTourSkip}
        onStepChange={handleStepChange}
        startAt={activeStep}
        className="cyberpunk-tour"
      />
    </div>
  );
};

export default TourExample;
