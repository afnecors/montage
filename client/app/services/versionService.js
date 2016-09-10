const VersionService = function($timeout, $mdTheming, themeProvider) {
  const versions = {
    gray: ['blue-grey', 'red'],
    green: ['green', 'red'],
    red: ['pink', 'red']
  };

  const service = {
    version: 'monuments',
    getVersion: getVersion,
    setVersion: setVersion
  };

  return service;

  ////

  function getVersion() {
    return service.version;
  }

  function setVersion(version) {
      themeProvider.theme(version)
        .primaryPalette(versions[version][0])
        .accentPalette(versions[version][1]);
      $mdTheming.generateTheme(version);
      themeProvider.setDefaultTheme(version);
      service.version = version;
  }
};

export default () => {
  angular
    .module('app')
    .factory('versionService', VersionService);
};
