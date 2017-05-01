import registerList from './list';
import registerNew from './new';

export default function (ngModule) {
  return Object.assign({}, registerList(ngModule),
                           registerNew(ngModule)
  );
}
