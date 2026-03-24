delete from sys_menu where name in ('AddS3Storage', 'EditS3Storage', 'DeleteS3Storage', 'UploadS3File');

delete from sys_menu where name = 'PluginS3';

drop table if exists s3_storage;

select setval(pg_get_serial_sequence('sys_menu', 'id'), coalesce(max(id), 0) + 1, true) from sys_menu;
