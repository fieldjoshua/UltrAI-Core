/**
 * Feature Discovery System
 *
 * Exports components and utilities for feature discovery and user progression.
 */

import { createExperienceTracker, ACTION_SCORES } from './experience_tracker';
import {
  createAchievementSystem,
  ACHIEVEMENT_TIERS,
} from './achievement_system';
import ProgressiveDisclosure from './ProgressiveDisclosure';
import AchievementNotification from './AchievementNotification';

export {
  createExperienceTracker,
  ACTION_SCORES,
  createAchievementSystem,
  ACHIEVEMENT_TIERS,
  ProgressiveDisclosure,
  AchievementNotification,
};
