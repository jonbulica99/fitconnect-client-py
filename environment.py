from enum import Enum


class Environment(Enum):
    DEV = 1, "The development environment (used internally by the FIT-Connect team)"
    TESTING = 2, "The test environment that can be used freely"
    STAGING = 3, "The staging environment to test update before deploying to production"
    PRODUCTION = 4, "The production environment"


ENV_CONFIG = {
    Environment.DEV: {
        'OAUTH_ENDPOINT': 'https://auth-dev.fit-connect.fitko.dev/token',
        'SUBMISSION_API': 'https://submission-api-dev.fit-connect.fitko.dev/v1',
    },
    Environment.TESTING: {
        'OAUTH_ENDPOINT': 'https://auth-testing.fit-connect.fitko.dev/token',
        'SUBMISSION_API': 'https://submission-api-testing.fit-connect.fitko.dev/v1',
    },
    Environment.STAGING: {
        'OAUTH_ENDPOINT': 'https://auth-refz.fit-connect.fitko.net/token',
        'SUBMISSION_API': 'https://submission-api-refz.fit-connect.niedersachsen.de/v1',
    },
    Environment.PRODUCTION: {
        'OAUTH_ENDPOINT': 'https://auth-prod.fit-connect.fitko.net/token',
        'SUBMISSION_API': 'https://submission-api-prod.fit-connect.niedersachsen.de/v1',
    }
}
