Alter table widgets alter COLUMN dashboard_id drop not null;
alter table widgets drop constraint "widgets_dashboard_id_fkey", add constraint "widgets_dashboard_id_fkey" FOREIGN KEY(dashboard_id) references dashboards(id) on delete cascade;