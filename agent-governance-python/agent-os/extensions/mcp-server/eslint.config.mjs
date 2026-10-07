import tseslint from '@typescript-eslint/eslint-plugin';

export default tseslint.configs['flat/recommended'].map((config) => ({
  ...config,
  files: ['src/**/*.ts'],
}));
