module.exports = {
    extends: ['@commitlint/config-conventional'],
    ignores: [(message) => message.startsWith('Initial commit')],
    // parserPreset: {
    // parserOpts: {
    //    issuePrefixes: ['[A-Z]{1,8}-[0-9]{1,4}'],
    //    referenceActions: null,
    //  },
    //},
    rules: {
      'footer-max-line-length': [0],
      'references-empty': [2, 'never'],
      'subject-case': [0],
      'type-case': [2, 'always', 'lower-case'],
    },
  };
