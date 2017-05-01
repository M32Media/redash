import template from './footer.html';
import logoUrl from '../../assets/images/m32-logo-small.png';

function controller(clientConfig, currentUser) {
  this.version = clientConfig.version;
  this.newVersionAvailable = clientConfig.newVersionAvailable && currentUser.isAdmin;
  this.logoUrl = logoUrl;
}

export default function (ngModule) {
  ngModule.component('footer', {
    template,
    controller,
  });
}
