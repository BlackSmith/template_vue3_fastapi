import Keycloak from 'keycloak-js';

const options = {
  url: KEYCLOAK_URL,
  clientId: KEYCLOAK_CLIENT_ID,
  realm: KEYCLOAK_REALM
}

const keycloak = new Keycloak(options);
let authenticated;
let store = null;
let refresh_timer = null;

/**
 * Initializes Keycloak, then run callback. This will prompt you to login.
 *
 * @param onAuthenticatedCallback
 */
async function init(onInitCallback) {
  try {
    authenticated = await keycloak.init({
      onLoad:  "check-sso",
      flow: 'standard',
      redirectUri: window.origin,
      pkceMethod: 'S256',
      refreshToken: localStorage.getItem('refreshToken'),
      // enableLogging: true,
      checkLoginIframe: true,
      silentCheckSsoRedirectUri: `${location.origin}/silent-check-sso.html`
    })
    onInitCallback()
  } catch (error) {
    console.error("Keycloak init failed")
    console.error(error)
  }
};

/**
 * Refreshes token
 */
async function refreshToken() {
  try {
    await keycloak.updateToken(60)
    return keycloak;
  } catch (error) {
    console.error('Failed to refresh token:', error);
  }
}


/**
 * Logout user
 */
function logout(url) {
  if (refresh_timer) {
    window.clearInterval(refresh_timer)
  }
  keycloak.logout({redirectUri: url});
}

/**
 * Login user
 */
function login() {
  return keycloak.login()
}

/**
 * Initializes store with Keycloak user data
 *
 */
async function initStore(storeInstance) {
  try {
    store = storeInstance
    store.initOauth(keycloak)

    // Show alert if user is not authenticated
    if (!authenticated) {
      console.warn("User not authenticated")
    } else {
      if (refresh_timer) {
          window.clearInterval(refresh_timer)
      }
      refresh_timer = window.setInterval(async () => {
        if (keycloak && keycloak.isTokenExpired(90)) {
          if (await refreshToken()) {
            store.initOauth(keycloak)
          } else {
            store.clearUserData()
            login()
          }
        }
      }, 60000)
    }
  } catch (error) {
    console.error("Keycloak init failed")
    console.error(error)
  }
};


const KeycloakService = {
  CallInit: init,
  CallInitStore: initStore,
  CallLogout: logout,
  CallLogin: login,
  CallTokenRefresh: refreshToken
};

export default KeycloakService;
