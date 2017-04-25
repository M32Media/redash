import registerList from './list';
import registerShow from './show';
import registerDataSources from './data-sources';
import registerEditGroupDialog from './edit-group-dialog';
import registerPermissions from './permissions';
import registerGroupName from './group-name';

export default function (ngModule) {
  registerEditGroupDialog(ngModule);
  registerGroupName(ngModule);

  return Object.assign({}, registerList(ngModule),
                           registerShow(ngModule),
                           registerPermissions(ngModule),
                           registerDataSources(ngModule));
}
