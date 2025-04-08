import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface ModelComparisonChartProps {
  models: string[];
  confidenceScores: number[];
  uniqueInsights: number[];
  responseTime: number[];
  colorTheme?: 'light' | 'dark';
}

/**
 * ModelComparisonChart visualizes the comparison between different AI models used in Ultra
 * It shows confidence scores, unique insights, and response times in a radar chart
 */
const ModelComparisonChart: React.FC<ModelComparisonChartProps> = ({
  models,
  confidenceScores,
  uniqueInsights,
  responseTime,
  colorTheme = 'light',
}) => {
  const chartRef = useRef<HTMLCanvasElement>(null);
  const chartInstance = useRef<Chart | null>(null);

  // Set colors based on theme
  const colors = {
    light: {
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      textColor: '#333',
      gridColor: 'rgba(0, 0, 0, 0.1)',
      pointBackgroundColors: [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(153, 102, 255, 0.8)',
      ],
      borderColors: [
        'rgba(54, 162, 235, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(255, 159, 64, 1)',
        'rgba(153, 102, 255, 1)',
      ],
    },
    dark: {
      backgroundColor: 'rgba(45, 55, 72, 0.8)',
      textColor: '#f7fafc',
      gridColor: 'rgba(255, 255, 255, 0.1)',
      pointBackgroundColors: [
        'rgba(56, 178, 255, 0.8)',
        'rgba(255, 109, 142, 0.8)',
        'rgba(85, 212, 212, 0.8)',
        'rgba(255, 179, 84, 0.8)',
        'rgba(163, 122, 255, 0.8)',
      ],
      borderColors: [
        'rgba(56, 178, 255, 1)',
        'rgba(255, 109, 142, 1)',
        'rgba(85, 212, 212, 1)',
        'rgba(255, 179, 84, 1)',
        'rgba(163, 122, 255, 1)',
      ],
    },
  };

  // Create theme-specific styles
  const themeColors = colors[colorTheme];

  useEffect(() => {
    if (chartRef.current) {
      // Destroy previous chart instance to prevent memory leaks
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        // Convert response time to a score (inverted since lower is better)
        // Assuming response time is in milliseconds and normalize to 0-100 scale
        const maxResponseTime = Math.max(...responseTime);
        const normalizedResponseTime = responseTime.map(
          (time) => 100 - (time / maxResponseTime) * 100
        );

        chartInstance.current = new Chart(ctx, {
          type: 'radar',
          data: {
            labels: ['Confidence', 'Unique Insights', 'Response Speed'],
            datasets: models.map((model, index) => ({
              label: model,
              data: [
                confidenceScores[index],
                uniqueInsights[index],
                normalizedResponseTime[index],
              ],
              backgroundColor:
                themeColors.pointBackgroundColors[
                  index % themeColors.pointBackgroundColors.length
                ],
              borderColor:
                themeColors.borderColors[
                  index % themeColors.borderColors.length
                ],
              borderWidth: 2,
              pointRadius: 5,
              pointHoverRadius: 7,
            })),
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: {
                  color: themeColors.textColor,
                  font: {
                    size: 14,
                  },
                },
              },
              tooltip: {
                backgroundColor: themeColors.backgroundColor,
                titleColor: themeColors.textColor,
                bodyColor: themeColors.textColor,
                titleFont: {
                  size: 14,
                  weight: 'bold',
                },
                bodyFont: {
                  size: 13,
                },
                padding: 10,
              },
            },
            scales: {
              r: {
                min: 0,
                max: 100,
                ticks: {
                  display: false,
                },
                pointLabels: {
                  color: themeColors.textColor,
                  font: {
                    size: 14,
                  },
                },
                grid: {
                  color: themeColors.gridColor,
                },
                angleLines: {
                  color: themeColors.gridColor,
                },
              },
            },
          },
        });
      }
    }

    // Cleanup function to destroy chart instance when component unmounts
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [models, confidenceScores, uniqueInsights, responseTime, colorTheme]);

  return (
    <div
      className="model-comparison-container"
      style={{ width: '100%', height: '400px' }}
    >
      <canvas ref={chartRef} />
    </div>
  );
};

export default ModelComparisonChart;
