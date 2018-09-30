// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

export const environment = {
  production: false,

  region: 'eu-central-1',
  identityPoolId: 'eu-central-1:5796c7bc-4913-4ef0-804c-3c2446036c61',
  userPoolId: 'eu-central-1_J1HZ86uLX',
  clientId: '6h58tr9l145ek8vqhqo9g3vi4d',

  apiAuth: 'https://ch9hjwfgck.execute-api.eu-central-1.amazonaws.com/auth',
  apiNoAuth: 'https://ch9hjwfgck.execute-api.eu-central-1.amazonaws.com/noauth'
};
