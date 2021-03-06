/* eslint-disable */
import { sortBy } from 'underscore';
import template from './dynamic-table.html';
import './dynamic-table.css';

function DynamicTable($sanitize) {
  'ngInject';
  this.itemsPerPage = this.count = this.format === 'short' ? 5 : 15;
  this.page = 1;
  this.rowsCount = 0;
  this.orderByField = undefined;
  this.orderByReverse = false;

  this.shortStyle = this.format === 'short' ? "short-table-pagination" : "";

  this.pageChanged = () => {
    const first = this.count * (this.page - 1);
    const last = this.count * (this.page);

    this.rowsToDisplay = this.rows.slice(first, last);
    // We need to exclude some columns in some special cases.
    this.columnsToDisplay = this.columns.filter((column) => {console.log(column);return column.name !== "Status__filter"});
  };

  this.$onChanges = (changes) => {
    if (changes.columns) {
      this.columns = changes.columns.currentValue;
    }

    if (changes.rows) {
      this.rows = changes.rows.currentValue;
    }

    this.rowsCount = this.rows.length;

    this.pageChanged();
  };

  //This aligns numbers to the left but could do other things in the future.
  this.getCellStyle = (data) => {
    if (typeof data === "number") {
      return "text-align:right";
    } else {
      return "";
    }
  }

  this.orderBy = (column) => {
    if (column === this.orderByField) {
      this.orderByReverse = !this.orderByReverse;
    } else {
      this.orderByField = column;
      this.orderByReverse = false;
    }

    if (this.orderByField) {
      this.rows = sortBy(this.rows, this.orderByField.name);
      if (this.orderByReverse) {
        this.rows = this.rows.reverse();
      }
      this.pageChanged();
    }
  };

  this.sanitize = value => $sanitize(value);

  this.sortIcon = (column) => {
    if (column !== this.orderByField) {
      return null;
    }

    if (this.orderByReverse) {
      return 'desc';
    }

    return 'asc';
  };
}

export default function (ngModule) {
  ngModule.component('dynamicTable', {
    template,
    controller: DynamicTable,
    bindings: {
      rows: '<',
      columns: '<',
      format: '<',
      count: '<',
    },
  });
}
