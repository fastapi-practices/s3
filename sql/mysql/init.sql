set @system_menu_id = (select id from sys_menu where name = 'System');

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values ('s3.menu', 'PluginS3', '/plugins/s3', 10, 'mdi:cloud-upload-outline', 1, '/plugins/s3/views/index', null, 1, 1, 1, '', null, @system_menu_id, now(), null);

set @s3_menu_id = LAST_INSERT_ID();

insert into sys_menu (title, name, path, sort, icon, type, component, perms, status, display, cache, link, remark, parent_id, created_time, updated_time)
values
('新增存储', 'AddS3Storage', null, 0, null, 2, null, 's3:storage:add', 1, 0, 1, '', null, @s3_menu_id, now(), null),
('修改存储', 'EditS3Storage', null, 0, null, 2, null, 's3:storage:edit', 1, 0, 1, '', null, @s3_menu_id, now(), null),
('删除存储', 'DeleteS3Storage', null, 0, null, 2, null, 's3:storage:del', 1, 0, 1, '', null, @s3_menu_id, now(), null),
('文件上传', 'UploadS3File', null, 0, null, 2, null, 's3:file:upload', 1, 0, 1, '', null, @s3_menu_id, now(), null);
