import registerList from './list';

export default function (ngModule) {
  return Object.assign({}, registerList(ngModule));
}
