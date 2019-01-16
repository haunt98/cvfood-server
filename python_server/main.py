import os
import sys
import psycopg2
import json
from flask import Flask, request, g
from datetime import date, datetime

app = Flask(__name__)
DATABASE_URL = os.environ['DATABASE_URL']


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(DATABASE_URL)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def getRawDataFromCur(cur):
    # chay query khong can tra ve
    if cur.description == None:
        return []

    # lay ten cua thuoc tinh
    attrs = []
    for attr in cur.description:
        attrs.append(attr[0])
    # lay du lieu tra ve
    query_result = cur.fetchall()

    # tao file json chua tung dong du lieu, ten thuoc tinh + gia tri
    rawData = []
    for row in query_result:
        row = list(row)
        for i in range(len(row)):
            # date, datetime -> string
            if isinstance(row[i], (date, datetime)):
                row[i] = row[i].isoformat()

        rawData.append(dict(zip(attrs, row)))

    return rawData


def query(queryStr, queryArgs=None, insertQuery=False):
    # connect sql
    cur = get_db().cursor()

    # query
    if queryArgs == None:
        cur.execute(queryStr)
    else:
        cur.execute(queryStr, queryArgs)
    if insertQuery == True:
        get_db().commit()

    # get raw data from query
    rawData = getRawDataFromCur(cur)

    # close connect
    cur.close()

    return rawData


def isValidAcc(type_acc):
    if type_acc == 'nguoi_dung' or type_acc == 'quan_an' or type_acc == 'shipper':
        return True
    return False


def isValidLogin():
    if request.args.get('sdt') != None and request.args.get('pass') != None:
        return True
    return False


def isValidSignup(type_acc):
    if request.args.get('sdt') == None or request.args.get('pass') == None \
    or request.args.get('ten') == None or request.args.get('email') == None:
        return False

    if type_acc == 'quan_an' and request.args.get('dchi') == None:
        return False

    if type_acc == 'shipper' and request.args.get('cmnd') == None:
        return False

    return True


def isValidDB(type_db):
    if isValidAcc(type_db):
        return True

    if type_db == 'hoa_don' or type_db == 'chi_tiet_hoa_don' \
    or type_db == 'mon_an' \
    or type_db == 'danh_gia' or type_db == 'yeu_thich':
        return True

    return False


@app.errorhandler(404)
def page_not_found(e):
    return 'Page not found'


@app.route('/')
def route_hello():
    return 'Hello'


@app.route('/login/<string:type_acc>')
def route_login(type_acc):
    if not isValidAcc(type_acc) or not isValidLogin():
        return json.dumps([])

    queryStr = """select * from %s where sdt = %%s and pass = %%s;""" % type_acc
    rawData = query(
        queryStr,
        queryArgs=(request.args.get('sdt', type=str),
                   request.args.get('pass', type=str)))
    return json.dumps(rawData, ensure_ascii=False)


@app.route('/signup/<string:type_acc>')
def route_signup(type_acc):
    if not isValidAcc(type_acc) or not isValidSignup(type_acc):
        return json.dumps([])

    # kiem tra acc ton tai
    queryStr = """select * from %s where sdt = %%s;""" % type_acc
    accWithSDT = query(
        queryStr, queryArgs=(request.args.get('sdt', type=str), ))
    if accWithSDT:  # da ton tai acc voi sdt nay
        return json.dumps([])

    # acc chua ton tai -> insert vao database
    if type_acc == 'quan_an':
        queryStr = """insert into %s (sdt, pass, ten, email, dchi, anh) values
        (%%s, %%s, %%s, %%s, %%s, 'https://i.imgur.com/DRv1Xng.jpg') returning *;""" % type_acc
        rawData = query(
            queryStr,
            queryArgs=(request.args.get('sdt', type=str),
                       request.args.get('pass', type=str),
                       request.args.get('ten', type=str),
                       request.args.get('email', type=str),
                       request.args.get('dchi', type=str)),
            insertQuery=True)
        return json.dumps(rawData, ensure_ascii=False)

    elif type_acc == 'shipper':
        queryStr = """insert into %s (sdt, pass, ten, email, cmnd, anh) values
        (%%s, %%s, %%s, %%s, %%s, 'https://i.imgur.com/OCa848u.jpg') returning *;""" % type_acc
        rawData = query(
            queryStr,
            queryArgs=(request.args.get('sdt', type=str),
                       request.args.get('pass', type=str),
                       request.args.get('ten', type=str),
                       request.args.get('email', type=str),
                       request.args.get('cmnd', type=str)),
            insertQuery=True)
        return json.dumps(rawData, ensure_ascii=False)

    else:
        queryStr = """insert into %s (sdt, pass, ten, email, anh) values
        (%%s, %%s, %%s, %%s, 'https://i.imgur.com/vuZ5wmt.png') returning *;""" % type_acc
        rawData = query(
            queryStr,
            queryArgs=(request.args.get('sdt', type=str),
                       request.args.get('pass', type=str),
                       request.args.get('ten', type=str),
                       request.args.get('email', type=str)),
            insertQuery=True)
        return json.dumps(rawData, ensure_ascii=False)


@app.route('/db/<string:type_db>')
def route_db(type_db):
    if not isValidDB(type_db):
        return json.dumps([])

    queryStr = """select * from %s;""" % type_db
    rawData = query(queryStr)
    return json.dumps(rawData, ensure_ascii=False)


@app.route('/mon_an')
def route_mon_an():
    if request.args.get('id_quan_an') == None:
        return json.dumps([])

    rawData = query(
        """select * from mon_an where id_quan_an = %s;""",
        queryArgs=(request.args.get('id_quan_an', type=int), ))
    return json.dumps(rawData, ensure_ascii=False)


@app.route('/hoa_don')
def route_hoa_don():
    # nothing
    if request.args.get('trangthai') == None \
    and request.args.get('id_nguoi_dung') == None \
    and request.args.get('id_quan_an') == None \
    and request.args.get('id_shipper') == None \
    and request.args.get('id_hoa_don') == None:
        return json.dumps(
            query("""select * from hoa_don;"""), ensure_ascii=False)

    # only id_hoa_don
    if request.args.get('trangthai') == None \
    and request.args.get('id_nguoi_dung') == None \
    and request.args.get('id_quan_an') == None \
    and request.args.get('id_shipper') == None \
    and request.args.get('id_hoa_don') != None:
        query_hoa_don = query(
            """select * from hoa_don where id = %s;""",
            queryArgs=(request.args.get('id_hoa_don', type=int), ))
        if not query_hoa_don:
            return json.dumps(None)
        return json.dumps(query_hoa_don[0], ensure_ascii=False)

    # only id_nguoi_dung
    if request.args.get('trangthai') == None \
    and request.args.get('id_nguoi_dung') != None \
    and request.args.get('id_quan_an') == None \
    and request.args.get('id_shipper') == None \
    and request.args.get('id_hoa_don') == None:
        return json.dumps(
            query(
                """select hoa_don.*, quan_an.dchi as dchi_quan
                from hoa_don join quan_an on hoa_don.id_quan_an = quan_an.id
                where id_nguoi_dung = %s
                order by id;""",
                queryArgs=(request.args.get('id_nguoi_dung', type=int), )),
            ensure_ascii=False)

    # trang thai (shipper yes or no)
    if request.args.get('trangthai') != None \
    and request.args.get('id_nguoi_dung') == None \
    and request.args.get('id_quan_an') == None \
    and request.args.get('id_hoa_don') == None:
        rawResult = []
        rawHoaDon = []
        if request.args.get('id_shipper') == None:
            rawHoaDon = query(
                """select * from hoa_don where trangthai = %s;""",
                queryArgs=(request.args.get('trangthai', type=int), ))
        else:
            rawHoaDon = query(
                """select * from hoa_don where trangthai = %s and id_shipper = %s;""",
                queryArgs=(request.args.get('trangthai', type=int),
                           request.args.get('id_shipper', type=int)))

        for row in rawHoaDon:
            dataPerRow = {}
            dataPerRow['hoa_don'] = row

            # lay info nguoi dung trong hoa don
            id_nguoi_dung_from_row = int(row.get('id_nguoi_dung'))
            rawNguoiDung = query(
                """select * from nguoi_dung where id = %s;""",
                queryArgs=(id_nguoi_dung_from_row, ))
            dataPerRow['nguoi_dung'] = rawNguoiDung[0]

            # lay info quan an trong hoa don
            id_quan_an_from_row = int(row.get('id_quan_an'))
            rawQuanAn = query(
                """select * from quan_an where id = %s;""",
                queryArgs=(id_quan_an_from_row, ))
            dataPerRow['quan_an'] = rawQuanAn[0]

            # lay info toan bo chi tiet thuoc hoa don
            id_hoa_don_from_row = int(row.get('id'))
            rawChiTiet = query(
                """select mon_an.ten, chi_tiet_hoa_don.soluong, chi_tiet_hoa_don.gia
                from chi_tiet_hoa_don join mon_an
                on chi_tiet_hoa_don.id_mon_an = mon_an.id
                where id_hoa_don = %s;""",
                queryArgs=(id_hoa_don_from_row, ))
            dataPerRow['chi_tiet'] = rawChiTiet

            rawResult.append(dataPerRow)

        return json.dumps(rawResult, ensure_ascii=False)

    # only id_quan_an
    if request.args.get('trangthai') == None \
    and request.args.get('id_nguoi_dung') == None \
    and request.args.get('id_quan_an') != None \
    and request.args.get('id_shipper') == None \
    and request.args.get('id_hoa_don') == None:
        return json.dumps(
            query(
                """select * from hoa_don where id_quan_an = %s;""",
                queryArgs=(request.args.get('id_quan_an', type=int), )),
            ensure_ascii=False)

    # id_quan_an and trangthai
    if request.args.get('trangthai') != None \
    and request.args.get('id_nguoi_dung') == None \
    and request.args.get('id_quan_an') != None \
    and request.args.get('id_shipper') == None \
    and request.args.get('id_hoa_don') == None:
        return json.dumps(
            query(
                """select * from hoa_don where id_quan_an = %s and trangthai = %s;""",
                queryArgs=(request.args.get('id_quan_an', type=int),
                           request.args.get('trangthai', type=int))),
            ensure_ascii=False)

    return json.dumps([])


@app.route('/hoa_don_chua_xong')
def route_hoa_don_chua_xong():
    if request.args.get('id_nguoi_dung') == None:
        return json.dumps([])

    return json.dumps(
        query(
            """select hoa_don.*, quan_an.dchi as dchi_quan
            from hoa_don join quan_an on hoa_don.id_quan_an = quan_an.id
            where trangthai != -1 and trangthai < 4 and id_nguoi_dung = %s
            order by id;""",
            queryArgs=(request.args.get('id_nguoi_dung', type=int), )),
        ensure_ascii=False)


@app.route('/chi_tiet_hoa_don')
def route_chi_tiet_hoa_don():
    if request.args.get('id_hoa_don') == None:
        return json.dumps([])

    return json.dumps(
        query(
            """select chi_tiet_hoa_don.*, mon_an.ten from chi_tiet_hoa_don
            join mon_an on chi_tiet_hoa_don.id_mon_an = mon_an.id
            where chi_tiet_hoa_don.id_hoa_don = %s;""",
            queryArgs=(request.args.get('id_hoa_don', type=int), )),
        ensure_ascii=False)


@app.route('/dat_mon', methods=['POST'])
def route_dat_mon():
    if request.is_json == True:
        tt_dat_mon = request.get_json()

        # log
        # print(tt_dat_mon)

        # them vao hoa don
        query_hoa_don = query(
            """insert into hoa_don (id_nguoi_dung, id_quan_an, dchi_giao, tg_nd_dat, trangthai, gia_vanchuyen)
            values (%s, %s, %s, (select now()), 0, 20000) returning *;""",
            queryArgs=(tt_dat_mon.get('id_khach'), tt_dat_mon.get('id_quan'),
                       tt_dat_mon.get('dchi_giao')),
            insertQuery=True)

        # them dchi quan an
        query_quan_an = query(
            """select dchi from quan_an where id = %s;""",
            queryArgs=(tt_dat_mon.get('id_quan'), ))

        rawResult = {'chi_tiet': [], 'dchi_quan': query_quan_an[0].get('dchi')}
        gia_hoa_don = 0

        for chi_tiet in tt_dat_mon.get('chi_tiet'):
            # lay gia tien
            query_mon_an = query(
                """select gia from mon_an where id = %s;""",
                queryArgs=(chi_tiet.get('id_mon'), ))
            gia_chi_tiet = query_mon_an[0].get('gia') * chi_tiet.get('sl')
            gia_hoa_don += gia_chi_tiet

            # them vao chi tiet hoa don
            query_chi_tiet = query(
                """insert into chi_tiet_hoa_don (id_hoa_don, id_mon_an, soluong, gia) values
                (%s, %s, %s, %s) returning *;""",
                queryArgs=(query_hoa_don[0].get('id'), chi_tiet.get('id_mon'),
                           chi_tiet.get('sl'), gia_chi_tiet),
                insertQuery=True)
            rawResult['chi_tiet'].append(query_chi_tiet[0])

        # update lai gia tien cho hoa don
        query_hoa_don_update = query(
            """update hoa_don set gia = %s where id = %s returning *;""",
            queryArgs=(gia_hoa_don, query_hoa_don[0].get('id')),
            insertQuery=True)
        rawResult['hoa_don'] = query_hoa_don_update[0]

        return json.dumps(rawResult, ensure_ascii=False)

    print('Khong nhan duoc post json')
    return json.dumps(None)


# 1 error
# 0 ok
@app.route('/quan_an/xac_nhan')
def route_quan_an_xac_nhan():
    if request.args.get('id_hoa_don') == None:
        return json.dumps({'status': 1})

    query_hoa_don = query(
        """select trangthai from hoa_don where id = %s;""",
        queryArgs=(request.args.get('id_hoa_don', type=int), ))
    # khong ton tai id_hoa_don
    if not query_hoa_don:
        return json.dumps({'status': 1})

    # trang thai phai = 0
    old_trangthai = query_hoa_don[0].get('trangthai')
    if old_trangthai != 0:
        return json.dumps({'status': 1})

    new_trangthai = 1
    # huy don hang
    if request.args.get('huy') != None \
    and request.args.get('huy', type=int) == 1:
        new_trangthai = -1

    query(
        """update hoa_don set trangthai = %s, tg_qa_xac_nhan = (select now ())
        where id = %s;""",
        queryArgs=(new_trangthai, request.args.get('id_hoa_don', type=int)),
        insertQuery=True)
    return json.dumps({'status': 0})


@app.route('/giao_hang')
def route_giao_hang():
    if request.args.get('id_shipper') == None \
    or request.args.get('id_hoa_don') == None \
    or request.args.get('trangthai') == None:
        return json.dumps({'status': 1})

    query_hoa_don = query(
        """select trangthai from hoa_don where id = %s;""",
        queryArgs=(request.args.get('id_hoa_don', type=int), ))
    old_trangthai = query_hoa_don[0].get('trangthai')
    new_trangthai = request.args.get('trangthai', type=int)
    # -1 la bi huy
    if old_trangthai == -1 or new_trangthai <= old_trangthai:
        return json.dumps({'status': 1})

    if new_trangthai == 2:
        ktra_shipper = query(
            """select * from hoa_don
            where (trangthai = 2 or trangthai = 3) and id_shipper = %s;""",
            queryArgs=(request.args.get('id_shipper', type=int), ))
        if ktra_shipper:  # shipper dang xu ly don hang khac
            return json.dumps({'status': 1})

        query(
            """update hoa_don set trangthai = %s, id_shipper = %s, tg_sh_xac_nhan_giao = (select now())
            where id = %s;""",
            queryArgs=(request.args.get('trangthai', type=int),
                       request.args.get('id_shipper', type=int),
                       request.args.get('id_hoa_don', type=int)),
            insertQuery=True)
    elif new_trangthai == 3:
        query(
            """update hoa_don set trangthai = %s, id_shipper = %s, tg_sh_xac_nhan_nhan_hang = (select now())
            where id = %s;""",
            queryArgs=(request.args.get('trangthai', type=int),
                       request.args.get('id_shipper', type=int),
                       request.args.get('id_hoa_don', type=int)),
            insertQuery=True)
    elif new_trangthai == 4:
        query(
            """update hoa_don set trangthai = %s, id_shipper = %s, tg_sh_giao_thanhcong = (select now())
            where id = %s;""",
            queryArgs=(request.args.get('trangthai', type=int),
                       request.args.get('id_shipper', type=int),
                       request.args.get('id_hoa_don', type=int)),
            insertQuery=True)

    return json.dumps({'status': 0})


@app.route('/quan_an/them_mon_an', methods=['POST'])
def route_quan_an_them_mon_an():
    if request.is_json == True:
        tt_mon_an = request.get_json()

        # log
        # print(tt_mon_an)

        # anh mac dinh
        if tt_mon_an.get('anh') == None or tt_mon_an.get('anh') == '':
            tt_mon_an['anh'] = 'https://i.imgur.com/7T29Xxp.jpg'

        query_mon_an = query(
            """insert into mon_an (id_quan_an, ten, gia, anh) values (%s, %s, %s, %s) returning *;""",
            queryArgs=(tt_mon_an.get('id_quan_an'), tt_mon_an.get('ten'),
                       tt_mon_an.get('gia'), tt_mon_an.get('anh')),
            insertQuery=True)

        return json.dumps(query_mon_an[0], ensure_ascii=False)

    print('Khong nhan duoc post json')
    return json.dumps(None)


@app.route('/quan_an/sua_mon_an', methods=['POST'])
def route_quan_an_sua_mon_an():
    if request.is_json == True:
        tt_mon_an = request.get_json()

        # log
        # print(tt_mon_an)

        resultId = query(
            """select * from mon_an where id= %s;""",
            queryArgs=(tt_mon_an.get('id'), ))
        if not resultId:  # khong ton tai mon an nay
            return json.dumps(None)

        # anh mac dinh
        if tt_mon_an.get('anh') == None or tt_mon_an.get('anh') == '':
            tt_mon_an['anh'] = 'https://i.imgur.com/7T29Xxp.jpg'

        query_mon_an = query(
            """update mon_an set id_quan_an = %s, ten = %s, gia = %s, anh = %s
            where id = %s returning *;""",
            queryArgs=(tt_mon_an.get('id_quan_an'), tt_mon_an.get('ten'),
                       tt_mon_an.get('gia'), tt_mon_an.get('anh'),
                       tt_mon_an.get('id')),
            insertQuery=True)

        return json.dumps(query_mon_an[0], ensure_ascii=False)

    print('Khong nhan duoc post json')
    return json.dumps(None)


@app.route('/quan_an/xoa_mon_an')
def route_quan_an_xoa_mon_an():
    if request.args.get('id_mon_an') == None:
        return json.dumps({'status': 1})

    resultId = query(
        """select * from mon_an where id = %s;""",
        queryArgs=(request.args.get('id_mon_an', type=int), ))
    if not resultId:  # khong ton tai mon an
        return json.dumps({'status': 1})

    query(
        """delete from mon_an where id = %s;""",
        queryArgs=(request.args.get('id_mon_an', type=int), ),
        insertQuery=True)
    return json.dumps({'status': 0})


@app.route('/yeu_thich/check')
def route_yeu_thich_check():
    if request.args.get('id_nguoi_dung') == None \
    or request.args.get('id_quan_an') == None:
        return json.dumps({'status': 1})

    query_yeu_thich = query(
        """select * from yeu_thich
        where id_nguoi_dung = %s and id_quan_an = %s;""",
        queryArgs=(request.args.get('id_nguoi_dung', type=int),
                   request.args.get('id_quan_an', type=int)))
    if not query_yeu_thich:  # khong yeu thich
        return json.dumps({'status': 1})
    return json.dumps({'status': 0})


@app.route('/yeu_thich/change')
def route_yeu_thich_change():
    if request.args.get('id_nguoi_dung') == None \
    or request.args.get('id_quan_an') == None:
        return json.dumps({'status': 1})

    query_yeu_thich = query(
        """select * from yeu_thich
        where id_nguoi_dung = %s and id_quan_an = %s;""",
        queryArgs=(request.args.get('id_nguoi_dung', type=int),
                   request.args.get('id_quan_an', type=int)))
    if not query_yeu_thich:  # khong yeu thich
        query(
            """insert into yeu_thich (id_nguoi_dung, id_quan_an) values (%s, %s);""",
            queryArgs=(request.args.get('id_nguoi_dung', type=int),
                       request.args.get('id_quan_an', type=int)),
            insertQuery=True)

    else:
        query(
            """delete from yeu_thich where id_nguoi_dung = %s and id_quan_an = %s;""",
            queryArgs=(request.args.get('id_nguoi_dung', type=int),
                       request.args.get('id_quan_an', type=int)),
            insertQuery=True)

    return json.dumps({'status': 0})


@app.route('/danh_gia', methods=['POST'])
def route_danh_gia():
    if request.is_json == True:
        tt_danh_gia = request.get_json()

        # log
        # print(tt_danh_gia)

        if tt_danh_gia.get('id_nguoi_dung') == None \
        or tt_danh_gia.get('id_quan_an') == None \
        or tt_danh_gia.get('tieu_de') == None \
        or tt_danh_gia.get('noi_dung') == None:
            return json.dumps({'status': 1})

        query_danh_gia = query(
            """select * from danh_gia where id_nguoi_dung = %s and id_quan_an = %s;""",
            queryArgs=(tt_danh_gia.get('id_nguoi_dung'),
                       tt_danh_gia.get('id_quan_an')))
        if query_danh_gia:  # da ton tai danh gia thi khong cho danh gia nua
            return json.dumps({'status': 1})

        query(
            """insert into danh_gia (id_nguoi_dung, id_quan_an, tieu_de, noi_dung) values (%s, %s, %s, %s);""",
            queryArgs=(tt_danh_gia.get('id_nguoi_dung'),
                       tt_danh_gia.get('id_quan_an'),
                       tt_danh_gia.get('tieu_de'),
                       tt_danh_gia.get('noi_dung')),
            insertQuery=True)

        return json.dumps({'status': 0})

    print('Khong nhan duoc post json')
    return json.dumps({'status': 1})


@app.route('/xem_danh_gia')
def route_xem_danh_gia():
    if request.args.get('id_quan_an') == None:
        return json.dumps([])

    return json.dumps(
        query(
            """select nguoi_dung.ten, nguoi_dung.anh, danh_gia.tieu_de, danh_gia.noi_dung
            from danh_gia join nguoi_dung on danh_gia.id_nguoi_dung = nguoi_dung.id
            where id_quan_an = %s;""",
            queryArgs=(request.args.get('id_quan_an', type=int), )),
        ensure_ascii=False)


@app.route('/update_avatar/<string:type_acc>')
def route_update_avatar(type_acc):
    if not isValidAcc(type_acc) \
    or request.args.get('id') == None \
    or request.args.get('anh') == None:
        return json.dumps({'status': 1})

    queryStrId = """select * from %s where id = %%s;""" % type_acc
    resultId = query(
        queryStrId, queryArgs=(request.args.get('id', type=int), ))
    if not resultId:  # khong ton tai acc nay
        return json.dumps({'status': 1})

    queryStrUpdate = """update %s set anh = %%s where id = %%s;""" % type_acc
    query(
        queryStrUpdate,
        queryArgs=(request.args.get('anh', type=str),
                   request.args.get('id', type=int)),
        insertQuery=True)
    return json.dumps({'status': 0})


@app.route('/update_pass/<string:type_acc>')
def route_update_pass(type_acc):
    if not isValidAcc(type_acc) \
    or request.args.get('id') == None \
    or request.args.get('old_pass') == None \
    or request.args.get('new_pass') == None:
        return json.dumps({'status': 1})

    quertStrId = """select * from %s where id = %%s and pass = %%s;""" % type_acc
    resultID = query(
        quertStrId,
        queryArgs=(request.args.get('id', type=int),
                   request.args.get('old_pass', type=str)))
    if not resultID:  # khong ton tai acc, hoac sai pass
        return json.dumps({'status': 1})

    queryStrUpdate = """update %s set pass = %%s where id = %%s;""" % type_acc
    query(
        queryStrUpdate,
        queryArgs=(request.args.get('new_pass', type=str),
                   request.args.get('id', type=int)),
        insertQuery=True)
    return json.dumps({'status': 0})


@app.route('/update/nguoi_dung', methods=['POST'])
def route_update_nguoi_dung():
    if request.is_json:
        tt_nguoi_dung = request.get_json()

        # log
        # print(tt_nguoi_dung)

        resultId = query(
            """select * from nguoi_dung where id = %s;""",
            queryArgs=(tt_nguoi_dung.get('id'), ))
        if not resultId:  # khong ton tai acc nay
            return json.dumps(None)

        resultUpdate = query(
            """update nguoi_dung
            set ten = %s, email = %s, dchi = %s, anh = %s, sdt = %s, pass = %s
            where id = %s
            returning *;""",
            queryArgs=(tt_nguoi_dung.get('ten'), tt_nguoi_dung.get('email'),
                       tt_nguoi_dung.get('dchi'), tt_nguoi_dung.get('anh'),
                       tt_nguoi_dung.get('sdt'), tt_nguoi_dung.get('pass'),
                       tt_nguoi_dung.get('id')),
            insertQuery=True)
        return json.dumps(resultUpdate[0], ensure_ascii=False)

    print('Khong nhan duoc post json')
    return json.dumps(None)


if __name__ == '__main__':
    app.run()