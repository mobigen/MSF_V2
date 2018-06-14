#!/bin/env python
#-*- coding:utf-8 -*-

import os
import signal
import sys
import time
import xml.dom.minidom

import API.M6 as M6

import Mobigen.Common.Log as Log;

Log.Init()

TERM = False

def signal_handler(inum, ifrm) :
	__LOG__.Trace("Catch Signal : %s" % inum)
	global TERM
	TERM = True

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT , signal_handler)
signal.signal(signal.SIGHUP , signal_handler)
signal.signal(signal.SIGPIPE, signal_handler)

def shutdown() :
	__LOG__.Trace("Call Shutdown!!")
	os._exit(1)

def pars(ixml) :
	lsum = []
	for nsum in xml.dom.minidom.parse(ixml).getElementsByTagName("Sum_info"):
		isum = {}
		isum["sumname"] = str(nsum.getElementsByTagName("Sumname")[0].childNodes[0].data)

		ncon = nsum.getElementsByTagName("Connection")[0]

		isum["connection"] = {}
		isum["connection"]["host"] = str(ncon.getAttribute("url" )).split("//")[1]
		isum["connection"]["user"] = str(ncon.getAttribute("user"))
		isum["connection"]["pass"] = str(ncon.getAttribute("pass"))
		isum["querys"] = []

		lque = []

		for nque in nsum.getElementsByTagName("Query"):
			iknd = str(nque.getAttribute("type"  ))
			ikey = str(nque.getAttribute("keys"  ))
			ival = str(nque.getAttribute("values"))
			ipos = str(nque.getAttribute("pos"   ))
			irng = str(nque.getAttribute("partition_range" ))
			ihin = str(nque.getAttribute("hint" ))
			summary_range = str(nque.getAttribute("sum_range" ))

			if iknd in ["UNIQUE", "HASH"]:
				if lque :
					isum["querys"].append(lque)
				lque = []

			ique = {}

			ique["type"  ] = iknd or "UNIQUE"
			ique["keys"  ] = ikey and [int(i) for i in ikey.split(",")] or []
			ique["values"] = ival and [int(i) for i in ival.split(",")] or []
			ique["pos"   ] = ipos and [int(i) for i in ipos.split(",")] or []
			ique["hint"  ] = ihin
			ique["partition_range" ] = irng or "5"
			ique["summary_range"] = summary_range or "5"

			ique["sql"   ] = str(nque.childNodes[0].data)
			ique["sql"   ] = str(nque.childNodes[0].data.encode("utf-8"))
			lque.append(ique)

			# for n in nque.childNodes:
			# 	if n.data.strip() == '': continue
			# 	try :
			# 		ique["sql"   ] = str(n.data)
			# 	except :
			# 		ique["sql"   ] = str(n.data.encode("utf-8"))
			# 	lque.append(ique)

		if  lque :

			isum["querys"].append(lque)

		lsum.append(isum)

	return lsum

def summ(istm, iptm, isum) :

	istm += '00'

	ihst = isum["connection"]["host"]
	iuid = isum["connection"]["user"]
	ipwd = isum["connection"]["pass"]

	conn = M6.Connection(ihst, iuid, ipwd)
	curs = conn.Cursor()

	curs.SetFieldSep ("|^|")
	curs.SetRecordSep("|&amp;|")

	join_hash = {}
	val_length = 0
	lrec = []

	for lque in isum["querys"] :

		ique = lque[0]
		ityp = ique["type"  ]
		ikey = ique["keys"  ]
		ival = ique["values"]
		irng = ique["partition_range" ] + '00'
		ihit = ique["hint"  ]
		isrn = ique["summary_range"]

		if isrn.lower() == "daily" :
			st_time = istm[:8] + "000000"
		elif isrn.lower() == "hourly" :
			st_time = istm[:10] + "0000"
		else :
			st_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.mktime(time.strptime(istm, "%Y%m%d%H%M%S")) - (int(isrn) * 60)))
		en_time = istm

		st_part = str(int(st_time) - (int(st_time) % int(irng)))
		en_part = str(int(en_time) - (int(en_time) % int(irng)))

		condition = "<" if st_part != en_part and en_part == en_time else "<="

		ipar = str(int(istm) - (int(istm) % (int(irng))))

		__LOG__.Trace("%s <= PARTITION AND PARTITION <= %s  where  %s <= TIMESTAMP AND TIMESTAMP <= %s" % (st_part, en_part, st_time, en_time))

		isql = "\n/*+ LOCATION ( '%s' <= PARTITION AND PARTITION %s '%s' %s ) */\n%s" % (st_part, condition, en_part, ihit, ique["sql"])

		isql = isql.replace("%stime", st_time)
		isql = isql.replace("%etime", en_time)
		isql = isql.replace("%pre_stime", iptm)
		isql = isql.replace("%cdate", istm[:8])
		isql = isql.replace("%ctime", istm[8:12])

		__LOG__.Trace(" ** SQL ** %s" % isql)
		curs.Execute2(isql)

		lres = [ires for ires in curs]

		__LOG__.Trace("lres length = %d" % (len(lres)))

		joined_key = dict()
		if ityp == "HASH":

			for row in lres :
				key = "|^|".join([str(row[idx]) for idx in ikey])
				val = [str(row[idx]) for idx in ival]

				try :
					if not joined_key.has_key(key):
						join_hash[key].extend(val)
						joined_key[key] = None
				except :
					join_hash[key] = [''] * val_length
					join_hash[key].extend(val)

			val_length += len(ival)
			for key in join_hash:
				if len(join_hash[key]) < val_length:
					join_hash[key].extend([''] * (val_length - len(join_hash[key])))

		else :
			lrec = lrec + lres

	lrec = lrec + [key.split("|^|") + join_hash[key] for key in join_hash]

	curs.Close()
	conn.close()

	__LOG__.Trace("lrec length = %d" % (len(lrec)))

	return lrec


def loop(lsum, idir) :

	__LOG__.Trace("strt loop...")

	while not TERM :

		try : line = sys.stdin.readline()
		except : break

		if not line : break

		line = line.rstrip()

		__LOG__.Trace("read %s" % (line))

		if not line.startswith("noti://") :
			__LOG__.Trace("Require Prefix 'noti://' : %s" % line)
			sys.stderr.write("%s\n" % line)
			sys.stderr.flush()
			continue

		istm = os.path.basename(line)[:12]

		if  not istm.isdigit() :

			sys.stderr.write("%s\n" % (line))
			sys.stderr.flush()

			continue

		iptm = time.strftime("%Y%m%d%H%M%S", time.localtime(time.mktime(time.strptime(istm, "%Y%m%d%H%M%S")) - 604800))

		st_time = time.time()

		for isum in lsum :

			sst_time = time.time()

			isnm = isum["sumname"]

			__LOG__.Trace("summ stime : %s  summ name : %s" % (istm, isnm))

			while not TERM :
				try :
					lrec = summ(istm, iptm, isum)
					break
				except :
					__LOG__.Exception()
					time.sleep(1)

			fime = os.path.join(idir, "%s_%s_%s_%s.dat" % (isnm, istm + "00", len(lrec), os.getpid()))

			fd = open(fime, "w")
			for irec in lrec : fd.write("\x1c".join([str(i) for i in irec]) + "\n")
			fd.close()

			sys.stdout.write("file://%s\n" % (fime))
			sys.stdout.flush()
			__LOG__.Trace("Std OUT : %s  Processing Time : %.2f" % (fime, (time.time() - sst_time)))

		__LOG__.Trace("Total Processing Time : %.2f" % (time.time() - st_time))

		sys.stderr.write("%s\n" % (line))
		sys.stderr.flush()

	__LOG__.Trace("stop loop...")


def main(args) :

	__LOG__.Trace("strt process")

	ixml, idir = args

	ixml = os.path.expanduser(ixml)
	idir = os.path.expanduser(idir)
	__LOG__.Trace("ixml %s" % (ixml))
	__LOG__.Trace("idir %s" % (idir))

	if not os.path.exists(idir):
		os.makedirs(idir)
	if not os.path.isdir(idir):
		print_function()
		sys.exit()

	loop(pars(ixml), idir)

	__LOG__.Trace("stop process")


def print_usage():
	print >> sys.stderr, "Usage : %s SUMMARY_NAME XML_FILE OUTPUT_DIR" % module
	print >> sys.stderr, "Exam  : %s CDR_SUMMARY_5M ~/SFMILOG/conf/IRIS_XML/CDR_SUMMARY.xml /DATA1/DEV/OUTPUT" % module


if  __name__ == "__main__" :
	module = os.path.basename(sys.argv[0])

	if  len(sys.argv) != 4:
		print_usage()
		sys.exit()

	log_file = "~/Columbus/log/%s_%s.log" % (os.path.basename(sys.argv[0]), sys.argv[1])
	Log.Init()

	try:
        main(sys.argv[2: ])
	except:
        __LOG__.Exception()
