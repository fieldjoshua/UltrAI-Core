"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

const progressVariants = cva(
  "relative w-full overflow-hidden rounded-full bg-secondary",
  {
    variants: {
      size: {
        default: "h-4",
        sm: "h-2",
        lg: "h-6"
      },
      variant: {
        default: "",
        interactive: "cursor-pointer hover:opacity-90",
        animated: "transition-all duration-300"
      }
    },
    defaultVariants: {
      size: "default",
      variant: "default"
    },
  }
)

export interface ProgressProps
  extends React.HTMLAttributes<HTMLDivElement>,
  VariantProps<typeof progressVariants> {
  value?: number
  max?: number
  animated?: boolean
  showLabels?: boolean
  labels?: string[]
  activeStep?: number
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, size, variant, animated = false, showLabels = false, labels = [], activeStep = 0, ...props }, ref) => {
    return (
      <div className="w-full space-y-2">
        <div
          ref={ref}
          className={cn(progressVariants({ size, variant, className }))}
          {...props}
        >
          {animated ? (
            <motion.div
              className="h-full bg-primary"
              style={{ width: "0%" }}
              animate={{ width: `${value}%` }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
            />
          ) : (
            <div
              className="h-full bg-primary transition-all"
              style={{ width: `${value}%` }}
            />
          )}

          {/* Step indicators for multi-step flows */}
          {labels.length > 0 && (
            <div className="absolute top-0 left-0 w-full h-full flex justify-between items-center px-1">
              {labels.map((_, index) => {
                const stepPosition = (index / (labels.length - 1)) * 100;
                const isActive = index <= activeStep;
                return (
                  <div
                    key={index}
                    className={cn(
                      "w-3 h-3 rounded-full -mt-0.5 relative z-10",
                      isActive ? "bg-white border border-primary" : "bg-secondary border border-muted-foreground"
                    )}
                    style={{ marginLeft: `${index === 0 ? 0 : stepPosition}%` }}
                  />
                );
              })}
            </div>
          )}
        </div>

        {/* Labels below progress bar */}
        {showLabels && labels.length > 0 && (
          <div className="flex justify-between text-xs text-muted-foreground px-1">
            {labels.map((label, index) => {
              const isActive = index <= activeStep;
              return (
                <div
                  key={index}
                  className={cn(
                    "transition-colors duration-300",
                    isActive ? "text-primary font-medium" : "text-muted-foreground"
                  )}
                >
                  {label}
                </div>
              );
            })}
          </div>
        )}
      </div>
    )
  }
)

Progress.displayName = "Progress"

export { Progress }