extern unsigned char M_BaseHTTPServer[];
extern unsigned char M_ConfigParser[];
extern unsigned char M_FixTk[];
extern unsigned char M_Mobigen[];
extern unsigned char M_Mobigen__Common[];
extern unsigned char M_Mobigen__Common__Log[];
extern unsigned char M_Mobigen__Common__Log__DummyLog[];
extern unsigned char M_Mobigen__Common__Log__PipeLog[];
extern unsigned char M_Mobigen__Common__Log__RotatingLog[];
extern unsigned char M_Mobigen__Common__Log__StandardErrorLog[];
extern unsigned char M_Mobigen__Common__Log__StandardLog[];
extern unsigned char M_Mobigen__Common__Log__UDPLog[];
extern unsigned char M_SocketServer[];
extern unsigned char M_StringIO[];
extern unsigned char M_Tkconstants[];
extern unsigned char M_Tkinter[];
extern unsigned char M_UserDict[];
extern unsigned char M___future__[];
extern unsigned char M___main__[];
extern unsigned char M__abcoll[];
extern unsigned char M__threading_local[];
extern unsigned char M_abc[];
extern unsigned char M_atexit[];
extern unsigned char M_base64[];
extern unsigned char M_bdb[];
extern unsigned char M_bisect[];
extern unsigned char M_cmd[];
extern unsigned char M_codecs[];
extern unsigned char M_collections[];
extern unsigned char M_copy[];
extern unsigned char M_copy_reg[];
extern unsigned char M_ctypes[];
extern unsigned char M_ctypes___endian[];
extern unsigned char M_difflib[];
extern unsigned char M_dis[];
extern unsigned char M_distutils[];
extern unsigned char M_distutils__dep_util[];
extern unsigned char M_distutils__errors[];
extern unsigned char M_distutils__log[];
extern unsigned char M_distutils__spawn[];
extern unsigned char M_distutils__sysconfig[];
extern unsigned char M_distutils__text_file[];
extern unsigned char M_distutils__util[];
extern unsigned char M_doctest[];
extern unsigned char M_dummy_thread[];
extern unsigned char M_dummy_threading[];
extern unsigned char M_email[];
extern unsigned char M_email___parseaddr[];
extern unsigned char M_email__base64mime[];
extern unsigned char M_email__charset[];
extern unsigned char M_email__encoders[];
extern unsigned char M_email__errors[];
extern unsigned char M_email__feedparser[];
extern unsigned char M_email__generator[];
extern unsigned char M_email__header[];
extern unsigned char M_email__iterators[];
extern unsigned char M_email__message[];
extern unsigned char M_email__mime[];
extern unsigned char M_email__parser[];
extern unsigned char M_email__quoprimime[];
extern unsigned char M_email__utils[];
extern unsigned char M_encodings[];
extern unsigned char M_encodings__aliases[];
extern unsigned char M_fnmatch[];
extern unsigned char M_formatter[];
extern unsigned char M_ftplib[];
extern unsigned char M_functools[];
extern unsigned char M_genericpath[];
extern unsigned char M_getopt[];
extern unsigned char M_getpass[];
extern unsigned char M_gettext[];
extern unsigned char M_glob[];
extern unsigned char M_hashlib[];
extern unsigned char M_heapq[];
extern unsigned char M_hmac[];
extern unsigned char M_httplib[];
extern unsigned char M_inspect[];
extern unsigned char M_keyword[];
extern unsigned char M_linecache[];
extern unsigned char M_locale[];
extern unsigned char M_logging[];
extern unsigned char M_logging__handlers[];
extern unsigned char M_macurl2path[];
extern unsigned char M_mimetools[];
extern unsigned char M_mimetypes[];
extern unsigned char M_ntpath[];
extern unsigned char M_nturl2path[];
extern unsigned char M_opcode[];
extern unsigned char M_optparse[];
extern unsigned char M_os[];
extern unsigned char M_os2emxpath[];
extern unsigned char M_pdb[];
extern unsigned char M_pickle[];
extern unsigned char M_pkgutil[];
extern unsigned char M_posixpath[];
extern unsigned char M_pprint[];
extern unsigned char M_py_compile[];
extern unsigned char M_pydoc[];
extern unsigned char M_pydoc_topics[];
extern unsigned char M_quopri[];
extern unsigned char M_random[];
extern unsigned char M_re[];
extern unsigned char M_repr[];
extern unsigned char M_rfc822[];
extern unsigned char M_shlex[];
extern unsigned char M_site[];
extern unsigned char M_smtplib[];
extern unsigned char M_socket[];
extern unsigned char M_sre_compile[];
extern unsigned char M_sre_constants[];
extern unsigned char M_sre_parse[];
extern unsigned char M_ssl[];
extern unsigned char M_stat[];
extern unsigned char M_string[];
extern unsigned char M_struct[];
extern unsigned char M_subprocess[];
extern unsigned char M_tempfile[];
extern unsigned char M_textwrap[];
extern unsigned char M_threading[];
extern unsigned char M_token[];
extern unsigned char M_tokenize[];
extern unsigned char M_traceback[];
extern unsigned char M_tty[];
extern unsigned char M_types[];
extern unsigned char M_unittest[];
extern unsigned char M_urllib[];
extern unsigned char M_urlparse[];
extern unsigned char M_uu[];
extern unsigned char M_warnings[];
extern unsigned char M_webbrowser[];

#include "Python.h"

static struct _frozen _PyImport_FrozenModules[] = {
	{"BaseHTTPServer", M_BaseHTTPServer, 21910},
	{"ConfigParser", M_ConfigParser, 24083},
	{"FixTk", M_FixTk, 1989},
	{"Mobigen", M_Mobigen, -880},
	{"Mobigen.Common", M_Mobigen__Common, -130},
	{"Mobigen.Common.Log", M_Mobigen__Common__Log, -3185},
	{"Mobigen.Common.Log.DummyLog", M_Mobigen__Common__Log__DummyLog, 1861},
	{"Mobigen.Common.Log.PipeLog", M_Mobigen__Common__Log__PipeLog, 6787},
	{"Mobigen.Common.Log.RotatingLog", M_Mobigen__Common__Log__RotatingLog, 6889},
	{"Mobigen.Common.Log.StandardErrorLog", M_Mobigen__Common__Log__StandardErrorLog, 6551},
	{"Mobigen.Common.Log.StandardLog", M_Mobigen__Common__Log__StandardLog, 6497},
	{"Mobigen.Common.Log.UDPLog", M_Mobigen__Common__Log__UDPLog, 6812},
	{"SocketServer", M_SocketServer, 23453},
	{"StringIO", M_StringIO, 11771},
	{"Tkconstants", M_Tkconstants, 2252},
	{"Tkinter", M_Tkinter, 207893},
	{"UserDict", M_UserDict, 9514},
	{"__future__", M___future__, 4373},
	{"__main__", M___main__, 16286},
	{"_abcoll", M__abcoll, 23078},
	{"_threading_local", M__threading_local, 6503},
	{"abc", M_abc, 5985},
	{"atexit", M_atexit, 2291},
	{"base64", M_base64, 11247},
	{"bdb", M_bdb, 19352},
	{"bisect", M_bisect, 3235},
	{"cmd", M_cmd, 14203},
	{"codecs", M_codecs, 37523},
	{"collections", M_collections, 6763},
	{"copy", M_copy, 11719},
	{"copy_reg", M_copy_reg, 5324},
	{"ctypes", M_ctypes, -20898},
	{"ctypes._endian", M_ctypes___endian, 2362},
	{"difflib", M_difflib, 61885},
	{"dis", M_dis, 6441},
	{"distutils", M_distutils, -445},
	{"distutils.dep_util", M_distutils__dep_util, 3248},
	{"distutils.errors", M_distutils__errors, 6630},
	{"distutils.log", M_distutils__log, 2731},
	{"distutils.spawn", M_distutils__spawn, 5688},
	{"distutils.sysconfig", M_distutils__sysconfig, 16155},
	{"distutils.text_file", M_distutils__text_file, 11425},
	{"distutils.util", M_distutils__util, 16629},
	{"doctest", M_doctest, 82259},
	{"dummy_thread", M_dummy_thread, 5615},
	{"dummy_threading", M_dummy_threading, 1303},
	{"email", M_email, -2952},
	{"email._parseaddr", M_email___parseaddr, 14073},
	{"email.base64mime", M_email__base64mime, 5408},
	{"email.charset", M_email__charset, 13678},
	{"email.encoders", M_email__encoders, 2512},
	{"email.errors", M_email__errors, 3731},
	{"email.feedparser", M_email__feedparser, 11524},
	{"email.generator", M_email__generator, 10642},
	{"email.header", M_email__header, 13738},
	{"email.iterators", M_email__iterators, 2455},
	{"email.message", M_email__message, 29194},
	{"email.mime", M_email__mime, -136},
	{"email.parser", M_email__parser, 3957},
	{"email.quoprimime", M_email__quoprimime, 9109},
	{"email.utils", M_email__utils, 9284},
	{"encodings", M_encodings, -4464},
	{"encodings.aliases", M_encodings__aliases, 8707},
	{"fnmatch", M_fnmatch, 3331},
	{"formatter", M_formatter, 20380},
	{"ftplib", M_ftplib, 28814},
	{"functools", M_functools, 1961},
	{"genericpath", M_genericpath, 3424},
	{"getopt", M_getopt, 6856},
	{"getpass", M_getpass, 4860},
	{"gettext", M_gettext, 16306},
	{"glob", M_glob, 2499},
	{"hashlib", M_hashlib, 4324},
	{"heapq", M_heapq, 12868},
	{"hmac", M_hmac, 4641},
	{"httplib", M_httplib, 36643},
	{"inspect", M_inspect, 38104},
	{"keyword", M_keyword, 2137},
	{"linecache", M_linecache, 3279},
	{"locale", M_locale, 47067},
	{"logging", M_logging, -53294},
	{"logging.handlers", M_logging__handlers, 39020},
	{"macurl2path", M_macurl2path, 2887},
	{"mimetools", M_mimetools, 8592},
	{"mimetypes", M_mimetypes, 17102},
	{"ntpath", M_ntpath, 11812},
	{"nturl2path", M_nturl2path, 1811},
	{"opcode", M_opcode, 5986},
	{"optparse", M_optparse, 56198},
	{"os", M_os, 27159},
	{"os2emxpath", M_os2emxpath, 4654},
	{"pdb", M_pdb, 45140},
	{"pickle", M_pickle, 40093},
	{"pkgutil", M_pkgutil, 19474},
	{"posixpath", M_posixpath, 11475},
	{"pprint", M_pprint, 10234},
	{"py_compile", M_py_compile, 6672},
	{"pydoc", M_pydoc, 93575},
	{"pydoc_topics", M_pydoc_topics, 401991},
	{"quopri", M_quopri, 6834},
	{"random", M_random, 25686},
	{"re", M_re, 13450},
	{"repr", M_repr, 5664},
	{"rfc822", M_rfc822, 32942},
	{"shlex", M_shlex, 7884},
	{"site", M_site, 18823},
	{"smtplib", M_smtplib, 30253},
	{"socket", M_socket, 15441},
	{"sre_compile", M_sre_compile, 11671},
	{"sre_constants", M_sre_constants, 6155},
	{"sre_parse", M_sre_parse, 20206},
	{"ssl", M_ssl, 15154},
	{"stat", M_stat, 2835},
	{"string", M_string, 20772},
	{"struct", M_struct, 245},
	{"subprocess", M_subprocess, 34838},
	{"tempfile", M_tempfile, 20319},
	{"textwrap", M_textwrap, 11966},
	{"threading", M_threading, 29516},
	{"token", M_token, 3902},
	{"tokenize", M_tokenize, 14234},
	{"traceback", M_traceback, 11813},
	{"tty", M_tty, 1351},
	{"types", M_types, 2696},
	{"unittest", M_unittest, 36296},
	{"urllib", M_urllib, 52451},
	{"urlparse", M_urlparse, 14792},
	{"uu", M_uu, 4299},
	{"warnings", M_warnings, 13356},
	{"webbrowser", M_webbrowser, 19349},

    {0, 0, 0} /* sentinel */
};

int
main(int argc, char **argv)
{
        extern int Py_FrozenMain(int, char **);

        PyImport_FrozenModules = _PyImport_FrozenModules;
        return Py_FrozenMain(argc, argv);
}

