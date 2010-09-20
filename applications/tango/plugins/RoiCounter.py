#    "$Name:  $";
#    "$Header:	$";
#=============================================================================
#
# file :	RoiCounter.py
#
# description : Python source for the RoiCounter and its commands. 
#		 The class is derived from Device. It represents the
#		 CORBA servant object which will be accessed from the
#		 network. All commands which can be executed on the
#		 RoiCounter are implemented in this file.
#
# project :	TANGO Device Server
#
# $Author:  $
#
# $Revision:  $
#
# $Log:	 $
#
# copyleft :	European Synchrotron Radiation Facility
#		BP 220, Grenoble 38043
#		FRANCE
#
#=============================================================================
#	   This file is generated by POGO
#    (Program Obviously used to Generate tango Object)
#
#	  (c) - Software Engineering Group - ESRF
#=============================================================================
#
import itertools
import weakref
import PyTango
import sys
import numpy
import processlib
from Lima import Core

try:
    import EdfFile
except ImportError:
    EdfFile = None

#==================================================================
#   RoiCounter Class Description:
#
#
#==================================================================


class RoiCounterDeviceServer(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------
    ROI_COUNTER_TASK_NAME = "RoiCounterTask"
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
	self.__roiCounterMgr = None
	PyTango.Device_4Impl.__init__(self,cl,name)
	RoiCounterDeviceServer.init_device(self)
        
    def __getattr__(self,name) :
        if name.startswith('is_') and name.endswith('_allowed') :
            self.__dict__[name] = self.__global_allowed
            return self.__global_allowed
        raise AttributeError('RoiCounterDeviceServer has no attribute %s' % name)

    def __global_allowed(self) :
        return self.get_state() == PyTango.DevState.ON

    def is_set_state_allowed(self) :
        return True

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
	pass


#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
	self.set_state(PyTango.DevState.OFF)
	self.get_device_properties(self.get_device_class())

    def set_state(self,state) :
	if(state == PyTango.DevState.OFF) :
	    if(self.__roiCounterMgr) :
		self.__roiCounterMgr = None
		ctControl = _control_ref()
		extOpt = ctControl.externalOperation()
		extOpt.delOp(self.ROI_COUNTER_TASK_NAME)
	elif(state == PyTango.DevState.ON) :
	    if not self.__roiCounterMgr:
                ctControl = _control_ref()
                extOpt = ctControl.externalOperation()
                self.__roiCounterMgr = extOpt.addOp(Core.ROICOUNTERS,self.ROI_COUNTER_TASK_NAME,0)
	PyTango.Device_4Impl.set_state(self,state)

    def Start(self) :
	try:
	    self.set_state(PyTango.DevState.ON)
	except:
	    import traceback
	    traceback.print_exc()
    
    def Stop(self):
	self.set_state(PyTango.DevState.OFF)
#------------------------------------------------------------------
#    Read Threshold_value attribute
#------------------------------------------------------------------
    def read_BufferSize(self, attr):
	value_read = self.__roiCounterMgr.getBufferSize()
	attr.set_value(value_read)


#------------------------------------------------------------------
#    Write Threshold_value attribute
#------------------------------------------------------------------
    def write_BufferSize(self, attr):
	data=[]
	attr.get_write_value(data)
        self.__roiCounterMgr.setBufferSize(data[0])



#==================================================================
#
#    RoiCounter command methods
#
#==================================================================
    def add(self,argin):
        if not len(argin) % 4:
            self.__roiCounterMgr.add(self.__get_roi_list_from_argin(argin))
        else:
            raise AttributeError('should be a roi vector as follow [x0,y0,width0,height0,x1,y1,width1,heigh1,...')
    
    def set(self,argin):
        if not len(argin) % 4:
            self.__roiCounterMgr.set(self.__get_roi_list_from_argin(argin))
        else:
            raise AttributeError('should be a roi vector as follow [x0,y0,width0,height0,x1,y1,width1,heigh1,...')

    
    def get(self):
        returnList = []
        for roi in self.__roiCounterMgr.get():
            p = roi.getTopLeft()
            s = roi.getSize()
            returnList.extend((p.x,p.y,s.getWidth(),s.getHeight()))
        return returnList

    def clearAllRoi(self):
        self.__roiCounterMgr.clearAllRoi()

    def setMaskFile(self,argin) :
        f = EdfFile.EdfFile(argin)
        data = f.GetData(0)
        mask = processlib.Data()
        mask.buffer = data
        self.__roiCounterMgr.setMask(mask)
    
    def readCounters(self,argin) :
        roiResultCounterList = self.__roiCounterMgr.readCounters(argin)
        if roiResultCounterList:
            minListSize = len(roiResultCounterList[0][1])
            for roiId,resultList in roiResultCounterList:
                if minListSize > len(resultList):
                    minListSize = len(resultList)

            
            if minListSize :
                returnArray = numpy.zeros(minListSize * len(roiResultCounterList) * 4 + 1,dtype = numpy.double)
                returnArray[0] = float(minListSize)
                indexArray = 1
                for roiId,resultList in roiResultCounterList:
                    for result in resultList[:minListSize] :
                        returnArray[indexArray:indexArray+4] = (float(result.frameNumber),
                                                                result.sum,
                                                                result.average,
                                                                result.std)
                        indexArray += 4
                return returnArray
        return numpy.array([],dtype = numpy.double)

    def __get_roi_list_from_argin(self,argin) :
        rois = []
        for x,y,w,h in itertools.izip(itertools.islice(argin,0,len(argin),4),
                                      itertools.islice(argin,1,len(argin),4),
                                      itertools.islice(argin,2,len(argin),4),
                                      itertools.islice(argin,3,len(argin),4)) :
            roi = Core.Roi(x,y,w,h)
            rois.append(roi)
        return rois
#==================================================================
#
#    RoiCounterClass class definition
#
#==================================================================
class RoiCounterDeviceServerClass(PyTango.DeviceClass):

    #	 Class Properties
    class_property_list = {
	}


    #	 Device Properties
    device_property_list = {
	}


    #	 Command definitions
    cmd_list = {
        'add':
        [[PyTango.DevVarLongArray,"roi vector [x0,y0,width0,height0,x1,y1,width1,heigh1,...]"],
         [PyTango.DevVoid,""]],
        'set':
        [[PyTango.DevVarLongArray,"roi vector [x0,y0,width0,height0,x1,y1,width1,heigh1,...]"],
	[PyTango.DevVoid,""]],
        'get':
        [[PyTango.DevVoid,""],
        [PyTango.DevVarLongArray,"roi vector [x0,y0,width0,height0,x1,y1,width1,heigh1,...]"]],
        'clearAllRoi':
        [[PyTango.DevVoid,""],
         [PyTango.DevVoid,""]],
        'setMaskFile':
        [[PyTango.DevVarStringArray,"Full path of mask file"],
         [PyTango.DevVoid,""]],
        'readCounters':
        [[PyTango.DevLong,"from which frame"],
         [PyTango.DevVarDoubleArray,"number of result for each roi,frame number 0,sum 0,average 0,std 0,frame number 0,sum 0,average 0,std 0..."]],
	'Start':
	[[PyTango.DevVoid,""],
	 [PyTango.DevVoid,""]],
	'Stop':
	[[PyTango.DevVoid,""],
	 [PyTango.DevVoid,""]],
	}


    #	 Attribute definitions
    attr_list = {
	'BufferSize':
	    [[PyTango.DevLong,
	    PyTango.SCALAR,
	    PyTango.READ_WRITE]],
	}


#------------------------------------------------------------------
#    RoiCounterDeviceServerClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
	PyTango.DeviceClass.__init__(self, name)
	self.set_type(name);



_control_ref = None
def set_control_ref(control_class_ref) :
    global _control_ref
    _control_ref= control_class_ref

def get_tango_specific_class_n_device() :
   return RoiCounterDeviceServerClass,RoiCounterDeviceServer
