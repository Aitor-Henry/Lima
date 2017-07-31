###########################################################################
# This file is part of LImA, a Library for Image Acquisition
#
#  Copyright (C) : 2009-2017
#  European Synchrotron Radiation Facility
#  BP 220, Grenoble 38043
#  FRANCE
# 
#  Contact: lima@esrf.fr
# 
#  This is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
# 
#  This software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################
import sys, os
import platform, multiprocessing
	
def check_options(options_pass):
	options_lima=[]
	options_script=[]
	for arg in options_pass:
		if arg=="--help" or arg=="-h" or arg=="-help" or arg=="-?":
			with open("INSTALL.txt", 'r') as f:
				print f.read()
			sys.exit()
		if "--prefix=" in arg:
			options_script.append(arg)
		elif arg=="-g" or arg=="--git":
			options_script.append("git")
		elif "--python-packages=" in arg:
			options_script.append(arg)
		else:
			options_lima.append(arg)
	return(options_script,options_lima)

def git_clone_submodule(submodules):
	submodules.append("third-party/Processlib")
	try:
		for submodule in submodules:
			if submodule not in not_submodule:
				if submodule in camera_list:
					submodule="camera/"+str(submodule)
				if submodule=="espia":
					submodule="camera/common/"+str(submodule)
				if submodule=="pytango-server":
					submodule="applications/tango/python"
				init_check = os.system("git submodule init " +str(submodule))
				if str(init_check)!="0":
					raise Exception("Couldn't init the following submodule : "+str(submodule))
		os.system("git submodule update")
		checkout_check = os.system("git submodule foreach 'git checkout cmake'")
		if str(checkout_check)!="0":
			raise Exception("Make sure every submodule has a branch cmake.")
	except Exception as inst:
				print inst
				if str(init_check)!="0":
					sys.exit(init_check)
				else:
					sys.exit(checkout_check)

def config_cmake_options(options):
	configFile = 'scripts/config.txt'
	option_name = []
	config_cmake = []
	for arg in options:
		if "camera/" in str(arg):
			option_name.append(str.upper(str(arg)[7:]))
		elif "third-party/" in str(arg):
			option_name.append(str.upper(str(arg)[12:]))
		elif arg=="pytango-server":
			option_name.append("PYTANGO_SERVER")
		else:
			#probably test or python options.
			option_name.append(str.upper(str(arg)))
	#return option in config.txt pass as argument and also the ones with "=1" in config.txt
	with open(configFile) as f:
		for line in f:
			line=line[:-1]
			for option in option_name:
				if option in line:
					line=line[:-1]
					line=line+str(1)
			if line.startswith('LIMA'):
				if line[len(line)-1]==str(1):
					config_cmake.append("-D"+line)
		config_cmake= " ".join([str(cmd) for cmd in config_cmake])
		return config_cmake
	f.close()

def install_lima_linux():
	os.chdir(os.getcwd()+"/build")
	try:
		if install_path=="" and install_python_path=="":
			cmake_check = os.system("cmake -G\"Unix Makefiles\" "+source_path+" "+cmake_config)
		else:
			if install_path!="" and install_python_path=="":
				cmake_check = os.system("cmake -G\"Unix Makefiles\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config)
			elif install_path=="" and install_python_path!="":
				cmake_check = os.system("cmake -G\"Unix Makefiles\" "+source_path+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
			else:
				cmake_check = os.system("cmake -G\"Unix Makefiles\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
		if str(cmake_check)!="0":
			raise Exception("Something is wrong in your CMake environement. Make sure your configuration is good.")

		#compilation_check= os.system("cmake --build . --target install")
		compilation_check = os.system("make -j"+str(multiprocessing.cpu_count()+1))
		if str(compilation_check)!="0":
			raise Exception("CMake couldn't build Lima. Contact claustre@esrf.fr for informations.")
		install_check = os.system("make install")
		if str(install_check)!="0":
			raise Exception("CMake couldn't install libraries. Make sure you have necessaries rights.")
	except Exception as inst:
		print inst
		if str(cmake_check)!="0":
			sys.exit(cmake_check)
		elif str(compilation_check)!="0":
			sys.exit(compilation_check)
		else:
			sys.exit(install_check)

def install_lima_windows():
	os.chdir(os.getcwd()+"/build")
	try :
		if platform.machine()=="AMD64":
			if install_path=="" and install_python_path=="":
				cmake_check = os.system("cmake -G\"Visual Studio 9 2008 Win64\" "+source_path+" "+cmake_config)
			else:
				if install_path!="" and install_python_path=="":
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008 Win64\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config)
				elif install_path=="" and install_python_path!="":
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008 Win64\" "+source_path+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
				else:
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008 Win64\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
		else:  #platform.machine()=="x86": should be 32bits.
			if install_path=="" and install_python_path=="":
				cmake_check = os.system("cmake -G\"Visual Studio 9 2008\" "+source_path+" "+cmake_config)
			else:
				if install_path!="" and install_python_path=="":
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config)
				elif install_path=="" and install_python_path!="":
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008\" "+source_path+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
				else:
					cmake_check = os.system("cmake -G\"Visual Studio 9 2008\" "+source_path+" -DCMAKE_INSTALL_PREFIX="+str(install_path)+" "+cmake_config+" -DPYTHON_SITE_PACKAGES_DIR="+str(install_python_path))
		if str(cmake_check)!="0":
			raise Exception("Something went wrong in the CMake preparation. Make sure your configuration is good.")

		compilation_check = os.system("cmake --build . --target install --config Release")
		if str(compilation_check)!="0":
			raise Exception("CMake couldn't build or install libraries. Contact claustre@esrf.fr for informations.")
	except Exception as inst:
		print inst
		if str(cmake_check)!="0":
			sys.exit(cmake_check)
		else:
			sys.exit(compilation_check)
			


if __name__ == '__main__':
	OS_TYPE=platform.system()
	del sys.argv[0]
	not_submodule=('git', 'python', 'tests', 'test', 'cbf', 'lz4', 'fits', 'gz', 'tiff', 'hdf5')
	camera_list=('adsc', 'andor3', 'basler', 'dexela', 'frelon', 'hexitec', 'marccd', 'merlin', 'mythen3', 'perkinelmer', 'pilatus', 'pointgrey', 'rayonixhs', 'ultra', 'xh', 'xspress3', 'andor', 'aviex', 'eiger', 'hamamatsu', 'imxpad', 'maxipix', 'mythen', 'pco', 'photonicscience','pixirad', 'prosilica', 'roperscientific', 'ueye', 'v4l2', 'xpad')
	install_path=""
	install_python_path=""
	print "OS TYPE : ",OS_TYPE
	source_path=os.getcwd()
	script_options, lima_options = check_options(sys.argv)

	#No git option under windows for obvious reasons.
	if OS_TYPE=="Linux":
		if "git" in script_options:
                        git_clone_submodule(lima_options)

	cmake_config = config_cmake_options(lima_options)
	print cmake_config
	for option in script_options:
		if "--prefix=" in option:
			install_path=option[9:]
		if "--python-packages=" in option:
			install_python_path=option[18:]
	if OS_TYPE=="Linux":
		install_lima_linux()
		
	elif OS_TYPE=="Windows":
		install_lima_windows()

	
