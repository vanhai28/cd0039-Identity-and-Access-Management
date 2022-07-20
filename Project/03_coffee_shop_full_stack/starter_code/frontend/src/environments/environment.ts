/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-82fpdm3y.us', // the auth0 domain prefix
    audience: 'https:/test/api', // the audience set for the auth0 app
    clientId: 'qaKQ1I9M8tX67Dg1Ygu7YMvojNvVbuDp', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application. 
  }
};
