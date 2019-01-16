set client_encoding to 'utf8';

create table nguoi_dung (
    id serial,
    ten text,
    email text,
    sdt text,
    pass text,
    dchi text,
    anh text,
    primary key (id)
);

create table quan_an (
    id serial,
    ten text,
    email text,
    sdt text,
    pass text,
    dchi text,
    anh text,
    primary key (id)
);

create table shipper (
    id serial,
    ten text,
    email text,
    sdt text,
    pass text,
    anh text,
    cmnd text,
    primary key (id)
);

create table mon_an (
    id serial,
    id_quan_an integer,
    ten text,
    gia bigint,
    mota text,
    anh text,
    primary key (id)
);

create table danh_gia (
    id_nguoi_dung integer,
    id_quan_an integer,
    tieu_de text,
    noi_dung text,
    primary key (id_nguoi_dung, id_quan_an)
);

create table yeu_thich (
    id_nguoi_dung integer,
    id_quan_an integer,
    primary key (id_nguoi_dung, id_quan_an)
);

create table hoa_don (
    id serial,
    dchi_giao text,
    id_nguoi_dung integer,
    id_quan_an integer,
    id_shipper integer,
    gia bigint,
    tg_nd_dat timestamp,
    tg_qa_xac_nhan timestamp,
    tg_sh_xac_nhan_giao timestamp,
    tg_sh_xac_nhan_nhan_hang timestamp,
    tg_sh_giao_thanhcong timestamp,
    trangthai integer,
    gia_vanchuyen bigint,
    primary key (id)
);

create table chi_tiet_hoa_don (
    id serial,
    id_hoa_don integer,
    id_mon_an integer,
    soluong integer,
    gia bigint,
    primary key (id)
);

insert into nguoi_dung (ten, sdt, pass, dchi, anh) values
    ('Người dùng 1', '01', '0',  '227 Nguyễn Văn Cừ, Quận 5, TP HCM', 'https://i.imgur.com/K0U9u1f.jpg'),
    ('Người dùng 2', '02', '0', '268 Lý Thường Kiệt, Quận 10, TP HCM ', 'https://i.imgur.com/UJdJPvN.jpg');

insert into quan_an (ten, sdt, pass, dchi, anh) values
    ('Quán ăn 1', '01', '0', '10 Đinh Tiên Hoàng, Quận 1, TP HCM', 'https://i.imgur.com/2BdLpIv.jpg'),
    ('Quán ăn 2', '02', '0', '2 Nguyễn Tất Thành, Quận 4, TP HCM', 'https://i.imgur.com/cg9Gzpx.jpg');

insert into mon_an (id_quan_an, ten, gia, anh) values
    (1, 'Món ăn 1', 10000, 'https://i.imgur.com/O01T2n2.jpg'),
    (1, 'Món ăn 2', 20000, 'https://i.imgur.com/NfkKUKM.jpg'),
    (2, 'Món ăn 3', 50000, 'https://i.imgur.com/MTME6zt.jpg'),
    (2, 'Món ăn 4', 40000, 'https://i.imgur.com/RgcwML5.jpg');

insert into shipper (ten, sdt, pass, cmnd, anh) values
    ('Shipper 1', '01', '0', 'CMND01', 'https://i.imgur.com/OCa848u.jpg'),
    ('Shipper 2', '02', '0', 'CMND02', 'https://i.imgur.com/OCa848u.jpg');