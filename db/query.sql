create table notes(
	id int primary key auto_increment,
    title varchar(500) not null,
    content text not null,
    is_completed tinyint default 0,
    folder_id int default null,
    created_at datetime not null default current_timestamp(),
    updated_at datetime not null default current_timestamp() on update now(),
    deleted_at datetime default null
);

create table folder(
	id int primary key auto_increment,
    name varchar(500) not null,
    created_at datetime not null default current_timestamp(),
    updated_at datetime not null default current_timestamp() on update now(),
    deleted_at datetime default null
);

alter table notes
ADD constraint FK_FolderId
foreign key(folder_id) references folder(id);


insert into notes(title,content) values 
('Note1','This is my first note'),
('Note2','This is my second note'),
('Note3','This is my third note'),
('Note4','This is my fourth note');

