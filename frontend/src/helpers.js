

export const formatDate = function (utcDateString) {
  const localDate = new Date(utcDateString);
  return localDate.toLocaleString();
}

export const camelToWords = function (str) {
  return str.charAt(0).toLowerCase() + str.slice(1).replace(/([A-Z])/g, ' $1').toLowerCase();
}

export const checkRightToRoute = function(auth, route) {
  if (route?.meta?.permission === undefined) {
    return true
  }
  if (!auth?.authenticated) {
    return false
  }
  if (typeof route?.meta?.permission === 'function') {
    return route.meta.permission(auth?.user?.permissions || [])
  }
  return auth.can(route?.meta?.permission) === true;
}
