
import pymysql
import time
import yaml
import json
from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)
db_config = config["mysql"]

def auth(token):
    if token is None:
            return False
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'SELECT * FROM vemular_auth WHERE `token` = %s;'
    cur.execute(sql,(token))
    results = cur.fetchall()
    if len(results) == 1:
        return True
    else:
        return False

def log(token,endpoint,response,msg):
    conn = pymysql.connect(**db_config)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    sql = 'INSERT INTO `vemular_api-logs` (`token`,`endpoint`,`response`,`msg`,`dt`) VALUES (%s,%s,%s,%s,%s)'
    dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(sql,(token,endpoint,response,msg,dt))

@app.route("/getData", methods=["GET","POST"])
def getData():
    res={}
    res["endpoint"] = "getData"

    if not auth(request.args.get("key")):
        res["code"]=0
        res["msg"]="Invalid API key"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    startdate = request.args.get("start")
    enddate = request.args.get("end")

    if not startdate or not enddate:
        res["code"]=0
        res["msg"]="Start and end dates are required"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    try:
        conn = pymysql.connect(**db_config)
        cur= conn.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT
                dpid,
                date_time,
                hex,
                flight_num,
                squawk,
                lat,
                lon,
                ST_AsText(geo_point) AS geo_point,
                fid,
                gs,
                alt_gps,
                alt_baro,
                cat,
                track,
                nav_heading
            FROM class_datapoints
            WHERE date_time BETWEEN %s AND %s
            ORDER BY date_time
            LIMIT 500
        """
        cur.execute(sql, (startdate, enddate))
        rows = cur.fetchall()
        res["code"]=1
        res["msg"]="Successfully retrieved datapoints"
        res["Points"]=rows
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return jsonify(res)

    except Exception as e:
        res["code"]=0
        res["msg"]=str(e)
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)


@app.route("/countInPolygon", methods=["GET","POST"])
def countInPolygon():
    res={}
    res["endpoint"] = "countInPolygon"

    if not auth(request.args.get("key")):
        res["code"]=0
        res["msg"]="Invalid API key"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    polygon = request.args.get("polygon")

    if not polygon:
        res["code"]=0
        res["msg"]="Polygon is required"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    try:
        coordinates = polygon.split(",")

        if len(coordinates) < 4:
            res["code"]=0
            res["msg"]="At least 4 coordinate pairs are required"
            log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
            return json.dumps(res,indent=4)
            
        points = []

        for coordinate in coordinates:

            values = coordinate.strip().split()

            if len(values) != 2:
                res["code"]=0
                res["msg"]="Invalid polygon coordinates"
                log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
                return json.dumps(res,indent=4)

            longitude = float(values[0])
            latitude = float(values[1])

            if not (-180 <= longitude <= 180 and
                    -90 <= latitude <= 90):
                res["code"]=0
                res["msg"]="Coordinates out of range"
                log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
                return json.dumps(res,indent=4)

            points.append(f"{longitude} {latitude}")

        if points[0] != points[-1]:
            res["code"]=0
            res["msg"]="Polygon must be closed"
            log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
            return json.dumps(res,indent=4)

        wkt_polygon = "POLYGON((" + ",".join(points) + "))"

        conn = pymysql.connect(**db_config)

        cur= conn.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT COUNT(*) AS total
            FROM class_datapoints
            WHERE ST_Within(
                geo_point,
                ST_GeomFromText(%s, 0)
            )
        """

        cur.execute(sql, (wkt_polygon,))
        result = cur.fetchone()

        res["code"]=1
        res["msg"]="Successfully counted datapoints"
        res["count"]=result["total"]
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)
        
    except ValueError:
        res["code"]=0
        res["msg"]="Invalid polygon coordinates"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    except Exception as e:
        res["code"]=0
        res["msg"]=str(e)
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

@app.route("/getAvgSpeedByFlight", methods=["GET","POST"])
def getAvgSpeedByFlight():
    res={}
    res["endpoint"] = "getAvgSpeedByFlight"

    if not auth(request.args.get("key")):
        res["code"]=0
        res["msg"]="Invalid API key"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    startdate = request.args.get("start")
    enddate = request.args.get("end")
    
    if not startdate or not enddate:
        res["code"]=0
        res["msg"]="Start and end dates are required"
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    try:
        conn = pymysql.connect(**db_config)
        cur=conn.cursor(pymysql.cursors.DictCursor) 
        sql = """
            SELECT
                AVG(gs) AS avg_speed,
                flight_num
            FROM class_datapoints
            WHERE date_time BETWEEN %s AND %s
            GROUP BY flight_num
            ORDER BY flight_num
            LIMIT 500
        """
        cur.execute(sql, (startdate, enddate))
        rows = cur.fetchall()
        for row in rows:
            if row["avg_speed"] is not None:
                row["avg_speed"] = float(row["avg_speed"])

        res["code"]=1
        res["msg"]="Successfully calculated average speed by flight"
        res["flights"]=rows
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)

    except Exception as e:
        res["code"]=0
        res["msg"]=str(e)
        log(request.args.get("key"),res["endpoint"],res["code"],res["msg"])
        return json.dumps(res,indent=4)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
