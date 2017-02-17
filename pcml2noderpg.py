#python3 pcml2noderpg.py -h                                        
# Usage: python3 pcml2noderpg.py -i <pcmlfilename> -t <REST type (post/get)> -o <jsfilename>  
#python3 pcml2noderpg.py -i /home/pcml/ftjprem.pcml -t get -o /node/ftjprem.js
import re
import sys, getopt
def main(argv):
	try:
		opts, args = getopt.getopt(argv,"h:i:t:o:",["pcmlfilename" , "resttype" , "jsfilename"])
	except getopt.GetoptError:
		print('Usage: pcml2noderpg.py -i <pcmlfilename> -t <REST type (post/get)> -o <jsfilename>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('Usage: pcml2noderpg.py -i <pcmlfilename> -t <REST type (post/get)> -o <jsfilename>')
			sys.exit()
		elif opt in ("-i", "--pcmlfilename"):
			pcmlfilename = arg		
		elif opt in ("-t", "--resttype"):
			resttype = arg			
		elif opt in ("-o", "--jsfilename"):
			jsfilename = arg
	#Search strings
	pgmname = 'program name'
	dataname = 'data name'
	datatypestruct = 'type="struct"'
	datatypechar = 'type="char"'
	# open file and read it into list
	#pcmlfilename = input('Enter a PCL filename ')
	#resttype     = input('Enter REST type (post/get)')
	#jsfilename   = input('Enter a result filename')
	inf = open(pcmlfilename,'r')
	outf= open(jsfilename,'w')
	lines = inf.readlines()
	# if the line has a program name tag 
	# 	add js statements
	for i in range(len(lines)):
		# Find program name
		#if (lines[i].rfind('</program>', 0, 50) > 0):   #Exit when end of program
			#print('Break 1')
			#break
		if (lines[i].rfind(pgmname, 0, 50) > 0):
			splitlist = lines[i].split('"')
			programname = splitlist[1]
			outf.write('Javascript code for the programCaller.js  \n')
			print('programCaller.js')
			outf.write('var xt = require(\'/QOpenSys/QIBM/ProdData/Node/os400/xstoolkit/lib/itoolkit\');\n')
			print('var xt = require(\'/QOpenSys/QIBM/ProdData/Node/os400/xstoolkit/lib/itoolkit\');')
			outf.write('var conn;\n')
			print('var conn;')
			outf.write('function init(){\n')
			print('function init(){')
			outf.write('  conn = new xt.iConn("*LOCAL");\n')
			print('  conn = new xt.iConn("*LOCAL");')
			outf.write('};\n')
			print('};')
			outf.write('function ' + 'run' + programname + '(programName, inputparm, cb){\n')
			print('function ' + 'run' + programname + '(programName, inputparm, cb){')
			outf.write('  var pgm = new xt.iPgm("' + programname + '");\n') 
			print('  var pgm = new xt.iPgm("' + programname + '");') 
			for j in range(len(lines)):
				j += i + 1		#Position to the start of parameter list
				if (lines[j].rfind('</program>', 0, 50) > 0):   #Exit when end of program
					break
				if (lines[j].rfind(dataname, 0, 50) > 0):    #Get the next data name	
					splitlist = lines[j].split('"')
					if (splitlist[2] == ' type=') and (splitlist[3] == 'char'):     #type char to be treated
						variablename = splitlist[1]
						length = splitlist[5]
						usage = splitlist[7] 
						outf.write('  pgm.addParam("","' + length + 'a");\n')
						print('  pgm.addParam("","1' + length + 'a");')
					if (splitlist[2] == ' type=') and (splitlist[3] == 'packed'):     #type packed to be treated
						variablename = splitlist[1]
						length = splitlist[5]
						precision = splitlist[7]
						usage = splitlist[9] 
						outf.write('  pgm.addParam("","' + length + 'p' + precision + '");\n')
						print('  pgm.addParam("","' + length + 'p' + precision + '");')					
					if (splitlist[2] == ' type=') and (splitlist[3] == 'zoned'):     #type zoned to be treated
						variablename = splitlist[1]
						length = splitlist[5]
						precision = splitlist[7]
						usage = splitlist[9] 
						outf.write('  pgm.addParam("","' + length + 'z' + precision + '");\n')
						print('  pgm.addParam("","' + length + 'z' + precision + '");')										
					if splitlist[4] == ' struct=':     #type struct to be treated
						structtag  = '<struct name="' + splitlist[5] + '">'
						structname = splitlist[5]
						variablename = splitlist[1]
						usage = splitlist[7] 
						outf.write('  var ' + variablename + '= [\n')
						print('  var ' + variablename + '= [')
						#print(structtag)
						for k in range(len(lines)):     #Loop to find the struct
							if (lines[k].rfind(structtag, 0, 50) > 0):  #Got the struct 
								#print('    //------------ ' + structname + ' --------------------')
								for m in range(len(lines)):  #Loop to find the fields in the struct
									m += k + 1		#Position to the start of fields in the struct
									if (lines[m].rfind('</struct>', 0, 50) > 0):
										break
									splitlist = lines[m].split('"')
									length = len(splitlist)
									if len(splitlist) > 3:
										fieldname = splitlist[1]
										if splitlist[3] == 'char':
											if (lines[m + 1].rfind('</struct>', 0, 50) > 0):
												#print('    //' + fieldname)
												outf.write('    ["", "' + splitlist[5] + 'A"]' + '     //' + fieldname + '\n')
												print('    ["", "' + splitlist[5] + 'A"]' + '     //' + fieldname)
											else:
												#print('    //' + fieldname)
												outf.write('    ["", "' + splitlist[5] + 'A"],' + '    //' + fieldname + '\n')
												print('    ["", "' + splitlist[5] + 'A"],' + '    //' + fieldname)
								outf.write('  ];\n')  #end of struct
								print('  ];')
								break
						if (usage == 'inputoutput'):
							outf.write('  pgm.addParam(' + variablename + ', {"io":"both", "len":"1"});\n')
							print('  pgm.addParam(' + variablename + ', {"io":"both", "len":"1"});')
						if (usage == 'input'):
							outf.write('  pgm.addParam(' + variablename + ', {"io":"in", "len":"1"});\n')
							print('  pgm.addParam(' + variablename + ', {"io":"in", "len":"1"});')
						if (usage == 'output'):
							outf.write('  pgm.addParam(' + variablename + ', {"io":"out", "len":"1"});\n')
							print('  pgm.addParam(' + variablename + ', {"io":"out", "len":"1"});')
					if (lines[j].rfind('</struct>', 0, 50) > 0):
						break		
			outf.write('  conn.add(pgm.toXML());\n')
			print('  conn.add(pgm.toXML());')
			outf.write('  conn.run(function (rsp) {\n')
			print('  conn.run(function (rsp) {')
			outf.write('    var results = xt.xmlToJson(rsp);\n')
			print('    var results = xt.xmlToJson(rsp);')
			outf.write('    return JSON.stringify(results[0].data);\n')
			print('    return JSON.stringify(results[0].data);')
			outf.write('  });\n')
			print('  });')
			outf.write('};\n')
			print('};')
			outf.write('module.exports.run' + programname +  ' = run' + programname + ';\n')
			print('module.exports.run' + programname +  ' = run' + programname + ';')
			outf.write('\n')
			print(' ')
			outf.write('\n')
			print(' ')
			outf.write('Javascript code for the server.js\n')
			print('server.js')
			outf.write('const programCaller = require(\'./programCaller.js\');\n')
			print('const programCaller = require(\'./programCaller.js\');')
			outf.write('programCaller.init();\n')
			print('programCaller.init();')
			#if (resttype == 'post'):
				#print('app.post(\'/run' + programname + '\', (req, res) => {')
				#print('  const urlParts = url.parse(req.url, true);')
				#print('});')
			if (resttype == 'get'):
				outf.write('app.get(\'/run' + programname + '\', (req, res) => {\n')
				print('app.get(\'/run' + programname + '\', (req, res) => {')
				outf.write('  const urlParts = url.parse(req.url, true);\n')
				print('  const urlParts = url.parse(req.url, true);')
				outf.write('  var program = urlParts.query.program;\n')
				print('  var program = urlParts.query.program;')
				outf.write('  var inputparm = urlParts.query.inputparm;\n')
				print('  var inputparm = urlParts.query.inputparm;')
				outf.write('  programCaller.run' + programname + '(program, inputparm, (results) =>{\n')
				print('  programCaller.run' + programname + '(program, inputparm, (results) =>{')
				outf.write('    res.writeHead(200, HEADER);\n')
				print('    res.writeHead(200, HEADER);')
				outf.write('    res.end(results);\n')
				print('    res.end(results);')
				outf.write('  });\n')
				print('  });')
				outf.write('});\n')
				print('});')
			outf.write('module.exports = app;')
			print('module.exports = app;')
	inf.close()
	outf.close()
if __name__ == "__main__":
	main(sys.argv[1:])