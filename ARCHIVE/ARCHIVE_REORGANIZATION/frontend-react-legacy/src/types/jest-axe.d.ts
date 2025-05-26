declare module 'jest-axe' {
  import { AxeResults, RunOptions, Spec } from 'axe-core';

  export interface Options extends RunOptions {
    rules?: {
      [key: string]: {
        enabled: boolean;
      };
    };
  }

  export function configureAxe(
    options?: Options
  ): (
    element: Element | string,
    axeOptions?: RunOptions,
    axeContext?: {}
  ) => Promise<AxeResults>;

  export function toHaveNoViolations(): {
    compare(actual: AxeResults): { pass: boolean; message: () => string };
  };

  export function axe(
    element: Element | string,
    options?: RunOptions,
    context?: {}
  ): Promise<AxeResults>;
}
