drop table if exists fics;
create table fics (
	id integer primary key autoincrement,
	title text not null,
	summary text not null,
	author text not null,
	url text not null,
        publishdate real not null,
	updatedate real not null
);

drop table if exists authors;
create table authors (
	id integer primary key autoincrement,
        name text not null
);
