#pragma once

#include <string>

//! \todo Which of the commands are deprecated and which are still needed (maybe in project only)?
//!       Is CalcAllSequence used?

#define DEF_ERP_msgUnvalid   -1 // not send from ERP
#define DEF_ERP_packet____    1
#define DEF_ERP_command___    2
#define DEF_ERP_data______    3
#define DEF_ERP_counter___    4

#define DEF_ERPCommandServerIsRunning_____  100 //!< sent if another server tries to start while we are running
#define DEF_ERPCommandexit________________  101 //!< exit the optimizer (with saving of status in xml files, as usual)
#define DEF_ERPCommandgetServerState______  102 //!< ask server to send it's status
#define DEF_ERPCommandERPTransferComplete_  103 //!< set server status (interface available), throw away deprecated xml files, send answer
#define DEF_ERPCommandbuildObjectModel____  104 //!< copy data from CommMgr to DataMgr production
#define DEF_ERPCommandbuildObjectModelCTP_  105 //!< copy data from CommMgr to DataMgr ctp
#define DEF_ERPCommandclearObjectModel____  106 //!< just delete all data in manager production
#define DEF_ERPCommandclearObjectModelCTP_  107 //!< just delete all data in manager ctp
//#define DEF_ERPCommandclearObjectPre______  108 //!< inactive, does nothing
#define DEF_ERPCommandclearObjectGround___  109 //!< just delete all data in manager grounddata
#define DEF_ERPCommandCheckErpID__________  110 //!< check received optimizer version against actual version of application (older app. is forbidden)
#define DEF_ERPCommandSetConfigParam______  111 //!< add the received configuration parameter to ApsConfig
#define DEF_ERPCommandPingServerState_____  112 //!< ping from erp to optimizer
#define DEF_ERPCommandLicensedModules_____  113 //!< list of licensed APS modules

#define DEF_ERPCommandoptimize____________  120 //!< start complete optimization
#define DEF_ERPCommandoptimizeCTP_________  121 //!< start single order (ctp) optimization
#define DEF_ERPCommandoptimizeSAP_________  122 //!< start single order (ctp) optimization, as early as possible
#define DEF_ERPCommandoptimizeCTPOverLoad_  123 //!< start single order (ctp) optimization, with overload // not used in erp anymore!!! only for compatibility to script left
#define DEF_ERPCommandoptimizeSAPOverLoad_  124 //!< start single order (ctp) optimization, as early as possible, with overload // not used in erp anymore!!! only for compatibility to script left

#define DEF_ERPCommandgetSolution_________  130 //!< send solution to erp (if not sent async. already)
#define DEF_ERPCommandgetSolutionCTP______  131 //!< send solution of ctp or of marked processes to erp
#define DEF_ERPCommandgetSolutionCtpProd__  132 //!< send solution of marked processes to erp (similar to above)
#define DEF_ERPCommandprintSolution_______  133 //!< write solution to console
#define DEF_ERPCommandexportSolutionXML___  134 //!< write solution to sdxl file
#define DEF_ERPCommandMarkForGetSolCtpProd  135 //!< mark the appended process number to write the solution for it (s. 131)

//#define DEF_ERPCommandsaveObjectModel_____  140 //!< inactive, does nothing
//#define DEF_ERPCommandloadObjectModel_____  141 //!< inactive, does nothing
//#define DEF_ERPCommandsaveInterface_______  142 //!< inactive, does nothing
//#define DEF_ERPCommandloadInterface_______  143 //!< inactive, does nothing
#define DEF_ERPCommandsaveServerKomplett__  144 //!< write status xml files to load at start (as "AfterOptimize") (via menu/p_vopt07.p)
//#define DEF_ERPCommandloadServerKomplett__  145 //!< inactive, never sent: load status xml files (from "AfterOptimize")

#define DEF_ERPCommandWriteToLog__________  149 //!< write message to optimizer logfile

#define DEF_ERPCommandsetServer___________  150 //!< use the appended general data for members in ApsServer (timestamp, etc.)
#define DEF_ERPCommandsetJobContext_______  151 //!< set job context (jobnr., dispo thereafter in erp or not, etc.)
#define DEF_ERPCommandsetJobContextCTP____  152 //!< set job context for ctp (with information about one order)
#define DEF_ERPCommandsetJobContextCTPProd  153 //!< set job context for ctp (for several orders, no info about order)

#define DEF_ERPCommanddeleteStackProcess__  160 //!< remove one denoted order from ctp datamanager, obsolete because contained in 161, which is called anyway
#define DEF_ERPCommanddeleteProcess_______  161 //!< remove one denoted order from all datamanagers, to be called before sending it anew
//#define DEF_ERPCommandmoveProcessToProd___  162 //!< inactive, not used, move one denoted order from ctp to production datamanager
//#define DEF_ERPCommandRenameProcessKey____  163 //!< inactive, not used, rename one denoted order in all datamanagers
#define DEF_ERPCommanddeleteProcessRueckNr  165 //!< delete denoted partprocess from ctp datamanager, obsolete because contained in 166, which is called anyway
#define DEF_ERPCommanddeleteStaProcRueckNr  166 //!< delete denoted partprocess from all datamanagers

#define DEF_ERPCommandupdateRessource_____  170 //!< update one denoted resource in ground datamanager
#define DEF_ERPCommandupdateCalendar______  171 //!< update one denoted calendar in ground datamanager
//#define DEF_ERPCommandupdateDepot_________  172 //!< inactive, does nothing and is not used
#define DEF_ERPCommandupdateCompanyCal____  173 //!< update all company calendar in ground datamanager

#define DEF_ERPCommandsend_Stammdaten_____  180 //!< set server status (only) to receiving master files
#define DEF_ERPCommandsend_Grunddaten_____  181 //!< set server status (only) to receiving ground data
#define DEF_ERPCommandsend_Auftrag_Ctp____  182 //!< set server status (only)
#define DEF_ERPCommandsend_alle_Auftraege_  183 //!< set server status (only)
#define DEF_ERPCommandsend_Calendar_______  184 //!< set server status (only)
#define DEF_ERPCommandsend_Depot__________  185 //!< set server status (only)
#define DEF_ERPCommandsend_Ressource______  186 //!< set server status (only)
#define DEF_ERPCommandsend_Standard_______  187 //!< set server status (only)
#define DEF_ERPCommandsend_Auftrag________  188 //!< logging only

#define DEF_ERPCommandResTransferComplete_  190 //!< set server status (only)
#define DEF_ERPCommandJobComplete_________  191 //!< set server status (only)

//#define DEF_ERPCommandCheckQueues_________  195 //!< inactive, not used
#define DEF_ERP_DataSyncDone______________  196 //!< fill context with datamanagers and increase optnr., mark all orders as optimized, do not optimize
#define DEF_ERP_OrderSyncDone_____________  197 //!< move data from CommMgr to DataMgr Production (to CtpMgr and then moving to ProdMgr)
#define DEF_ERP_CommandSendACMDone________  199 //!< all ACM-parameters have been send

/* ----------------------------------------------*/
/* admin Commands from ERP to ApsServerState     */
/* ----------------------------------------------*/

/* -----------------------------------------------------------------------------------------------*/
// this here was changed with task -------- PP-U-OPTI-027 --------
// but for compatibility to older versions, the deletion and aknowledge has to be kept! 
// even though the logic behind it is deleted

#define DEF_ERPCommandDeleteMessageQueue__  200 //!< start deleting message queue from this marker on until end marker is found
#define DEF_ERPCommandAckDelMessageQueue__  201 //!< tell ERP about starting deleting message queue
//#define DEF_ERPCommandQueueDeletionMarker_  202 //!< marker for end of message queue deletion
/* -----------------------------------------------------------------------------------------------*/

#define DEF_ERPCommandSetSimulationMode___  203 //!< begin simulation mode (try it)
#define DEF_ERPCommandAckSimulationMode___  204 //!< tell ERP about beginning simulation mode
#define DEF_ERPCommandDenySimulationMode__  205 //!< tell ERP about simulation mode forbidden (already started)
#define DEF_ERPCommandDelSimulationMode___  206 //!< stop simulation mode
#define DEF_ERPCommandAckDelSimulationMode  207 //!< tell ERP about stopping simulation mode


#define DEF_ERPCommandCommitSimulation____  210 //!< commit simulation mode by deleting saved data, stop simulation mode
#define DEF_ERPCommandRollbackSimulation__  211 //!< rollback simulation by transferring back saved data, stop simulation mode

#define DEF_ERPCommandCommitAPSSimulation_  220
#define DEF_ERPCommandDeleteAPSSimulation_  221

#define DEF_ERPCommandStartJobComplete____  250 //!< set status (only), server is not "newly started" then, declares start of co for messageWrite
#define DEF_ERPCommandEndOfJobComplete____  251 //!< inactive, does nothing
#define DEF_ERPCommandStartSimulationJob__  252 //!< start simulation mode by saving data for later restore
#define DEF_ERPCommandEndOfSimulationJob__  253 //!< inactive, does nothing
#define DEF_ERPCommandStartJobCTP_________  254 //!< declares start of a ctp, used for messageWrite
#define DEF_ERPCommandEndOfJobCTP_________  255 //!< inactive, does nothing

//#define DEF_ERPCommandStartSendSolution___  260 //!< inactive, does nothing and is not used
//#define DEF_ERPCommandEndOfSendSolution___  261 //!< inactive, does nothing and is not used
//#define DEF_ERPCommandAckSendSolution_____  262 //!< inactive, does nothing and is not used
//#define DEF_ERPCommandReSendSolution______  270 //!< inactive, does nothing and is not used

#define DEF_ERPCommandSetDatabaseID_______  280 //!< store denoted ERP database id, to ensure correct system connection later

//#define DEF_ERPCommandSONIC_TEST__________  299 //!< test command for internal checking of sonic connection

// ------------------------------------------------------------------------------
//  Create Table Objects
// ------------------------------------------------------------------------------
#define DEF_ERPCommandcreate_ApsTrMRPMovem  301 //!< used to receive denoted data type
//#define DEF_ERPCommandcreate_M_DispoBew___  301999 //!< deprecated name
//#define DEF_ERPCommandcreate_M_GewDurch___  302
//#define DEF_ERPCommandcreate_M_GewKap_____  303
//#define DEF_ERPCommandcreate_M_GewTermin__  304
//#define DEF_ERPCommandcreate_M_GewVerfr___  305
#define DEF_ERPCommandcreate_M_Kalender___  306 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_KalZeit____  307 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_KalDatum___  308 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_IntKal_____  309 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_Ressource__  311 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_RessAlt____  312 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_RessAltGr__  313 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_RessGruppe_  314 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_UebAdresse_  315 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_UebOrt_____  316 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_M_RessKombina  317 //!< used to receive denoted data type

#define DEF_ERPCommandcreate_P_ZeitMngEinh  320 //!< used to receive denoted data type

#define DEF_ERPCommandcreate_BetriebsKal__  322 //!< used to receive denoted data type

#define DEF_ERPCommandcreate_S_Artikel____  325 //!< used to receive denoted data type

#define DEF_ERPCommandcreate_ML_Artortvar_  330 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_ML_Artort____  331 //!< used to receive denoted data type
#define DEF_ERPCommandcreate_ML_Artortkomm  332 //!< used to receive denoted data type
//#define DEF_ERPCommandcreate_ML_Ort_______  333 //!< inactive, not used
#define DEF_ERPCommandcreate_ApsTrStock___  334

#define DEF_ERPCommandcreate_MD_Artikel___  335 //!< used to receive denoted data type (dispo params for part)

#define DEF_ERPCommandcreate_MC_Art_______  340 //!< used to receive denoted data type (charge type)
#define DEF_ERPCommandcreate_MC_Charge____  341 //!< used to receive denoted data type (charge)
#define DEF_ERPCommandcreate_MC_Lager_____  342 //!< used to receive denoted data type

#define DEF_ERPCommandcreate_Resource_____  350 //!< used to receive denoted data type (resource cosntraint)
#define DEF_ERPCommandcreate_Material_____  355 //!< used to receive denoted data type (material constraint)
#define DEF_ERPCommandcreate_Constraint___  360 //!< used to receive denoted data type (precedence constraint)
#define DEF_ERPCommandcreate_TimeConst____  361 //!< used to receive denoted data type (timebound constraint)
#define DEF_ERPCommandcreate_Activity_____  365 //!< used to receive denoted data type (activity)
#define DEF_ERPCommandcreate_ActivityRF___  366 //!< used to receive denoted data type (activity order information, not implemented completely)
#define DEF_ERPCommandcreate_Splitt_Act___  367 //!< used to receive denoted data type (ERP split points to allow breakable activities)
#define DEF_ERPCommandcreate_ContTimePoint  368 //!< used to receive denoted data type (split point because of continuous demand/supply)

#define DEF_ERPCommandcreate_Process______  370 //!< used to receive denoted data type (order, partorder)
#define DEF_ERPCommandcreate_Overload_Res_  375 //!< used to receive denoted data type (used overload information about resources)
#define DEF_ERPCommandcreate_Overload_Mat_  380 //!< used to receive denoted data type (used overload information about depots)
#define DEF_ERPCommandcreate_ProcessCst___  381 //!< used to receive denoted data type (constraint from one process to activity in other process)
#define DEF_ERPCommandcreate_Coverage_____  382 //!< used to receive denoted data type (coverages for a given process)
          // same as create_ProcessProd__

#define DEF_ERPCommandSetDatabaseTime_____  385 //!< receive denoted timestamp for time axis origin ("now" is 0 here)

/* update acitivies in server */
//#define DEF_ERPCommandupdate_Activity_____  390 //!< inactive, does nothing and not used in fact
#define DEF_ERPCommandupdate_Splitt_Act___  391 //!< inactive, does nothing and not used in fact
#define DEF_ERPCommandupdate_ContTimePoint  392 //!< inactive, does nothing and not used in fact
#define DEF_ERPCommandupdate_ActivityRF___  393 //!< inactive, does nothing and not used in fact
#define DEF_ERPCommandupdate_Resource_____  394 //!< inactive, does nothing and not used in fact


#define DEF_ERPCommandcreate_SetupMatrix__  395 //!< used to receive denoted data type (setup matrix)
#define DEF_ERPCommandcreate_SetupMatrixEn  396 //!< used to receive denoted data type  (setup matrix entry)
#define DEF_ERPCommandcreate_SetupPartFeat  397 //!< used to receive denoted data type (part setup feature)
#define DEF_ERPCommandcreate_SetupResFeat_  398 //!< used to receive denoted data type (resource setup feature)
#define DEF_ERPCommandcreate_SetupMatrixDf  399 //!< used to receive denoted data type (setup matrix definition)

// Clear data
// -----------------
#define DEF_ERPCommandclearERPTables______  400 //!< delete complete content of CommMgr (ground, master and process data)
//#define DEF_ERPCommanddel_Grunddaten______  401 //!< inactive, not used in fact, delete some content of CommMgr
//#define DEF_ERPCommanddel_Stammdaten______  402 //!< inactive, not used in fact, delete some content of CommMgr
#define DEF_ERPCommanddel__TR_Prozesse____  403 //!< delete process content of CommMgr
#define DEF_ERPCommanddel_SmallTables_____  404 //!< delete some content of CommMgr, sent just before sending this content
#define DEF_ERPCommanddel_AltResTables____  405 //!< delete information before getting new entries in alternative resources and groups
#define DEF_ERPCommanddel_CompanyCalendar_  406 //!< delete information before getting new entries in company calendar
#define DEF_ERPCommanddel_ResGrp__________  407 //!< delete information before getting new entries in resource group
#define DEF_ERPCommanddel_PlaceMatrix_____  408 //!< delete information before getting new entries in place matrix
#define DEF_ERPCommanddel_AddressMatrix___  409 //!< delete information before getting new entries in address matrix
#define DEF_ERPCommanddel_TimeQuantUnits__  410 //!< delete information before getting new entries in time quantity units
#define DEF_ERPCommanddel_ResCompMatrix___  411 //!< delete information before getting new entries in in resource compatibility matrix

// ---------------------------------------
//  commands APS-Server to APS-Server:
// ---------------------------------------
#define DEF_ERPCommandCheckForRunnigAPS___  700 //!< sent once while (re)connecting to sonic, to ensure there is no other server


// ---------------------------------------
//  commands APS-Server to ERP:
// ---------------------------------------
#define DEF_APSCommandackServerState______  800 //!< sending server status (after request)
#define DEF_APSCommandSetServerState______  801 //!< send actual server state to ERP
#define DEF_APSCommandcreateErpMessage____  802 //!< send data for a message to ERP (may be translated there via repository messages)

#define DEF_APSCommandackERPTransfer______  810 //!< sent after receiving complete data transfer (DEF_ERPCommandERPTransferComplete_)
#define DEF_APSCommandackObjectModelGen___  811 //!< sent after buildObjectModel
//#define DEF_APSCommandackOptimization_____  812 //!< inactive, does nothing and not used

#define DEF_APSCommandackSolution_________  820 //!< sent information: complete optimization result is sent
#define DEF_APSCommandackSolutionCTP______  821 //!< sent information: ctp optimization result is sent
#define DEF_APSCommandackSolutionCtpProd__  822 //!< sent information: ctp prod. (several orders) optimization result is sent
//#define DEF_APSCommandackSolutionBlock____  823 //!< sent after solution block has been sent // not used any more
#define DEF_APSCommandcreate_SchedInfo____  824 //!< send scheduling info 
#define DEF_APSCommandcreate_SchedTrigger_  825 //!< send demand proxy information
#define DEF_APSCommandackSolutionResult___  826 //!< sent after solution block has been sent 

#define DEF_APSCommandcreate_ContTimePoint  839 //!< sending information about continuous demand/supply
#define DEF_APSCommandcreate_MB_Aktivitaet  840 //!< sending activity data to ERP
#define DEF_APSCommandcreate_MB_Ressource_  841 //!< sending resource constraint (chosen alternative) to ERP
#define DEF_APSCommandcreate_MB_RessOverl_  842 //!< sending information about overload used in resource constraint
#define DEF_APSCommandcreate_MB_SplittAkt_  843 //!< sending information about split activities to ERP (optional)

//! sending overload information
#define DEF_APSCommanddelete_all_overload_  844 //!< sent before overload information for all activities will follow
#define DEF_APSCommandcreate_MA_SelUebRess  845 //!< sending overload resource constraint information
#define DEF_APSCommandcreate_MA_SelUebMat_  846 //!< sending overload material constraint information
#define DEF_APSCommandcreate_ActDispatch__  847 //!< sending activity dispatch interval information
#define DEF_APSCommandcreate_BufferInfo___  848 //!< sending process buffer information to ERP

#define DEF_APSCommandcreate_NoSoluitonPPA  850 //!< send info about process without solution (typo, but same in ERP, so we keep it)
#define DEF_APSCommandcreate_M_ServerKennZ  851 //!< sending statistical information about last optimization

//! tardiness reasoning - deprecated
//#define DEF_APSCommandcreate_ReasonXML____  852 //!< inactive, not used. send xml which contains all reasons of one process - obsolete, feature is not supported any more
//! commands for ReasonSendingFormat61
#define DEF_APSCommandcreate_ReasonStruc__  853 //!< send structure reason
#define DEF_APSCommandcreate_ReasonMat____  854 //!< send material reason
#define DEF_APSCommandcreate_ReasonRes____  855 //!< send resource reason
#define DEF_APSCommandcreate_ReasonAdmin__  856 //!< send information of kind of optimization (oveload material, throughput ...)
#define DEF_APSCommandcreate_ReasonTimebnd  857 //!< send timebound resason
#define DEF_APSCommandcreate_ReasonResRes_  858 //!< send incompatibility resource/resource reason (partial info)

#define DEF_APSCommandset_JobContext______  860 //!< sending job context back to ERP, at starting solution (jobnr, flag if dispo shall follow, etc.)
#define DEF_APSCommandset_JobContextCTP___  861 //!< sending job context back to ERP: ctp (one order)
#define DEF_APSCommandset_JobContextCTPPrd  862 //!< sending job context back to ERP: ctp (several orders)
#define DEF_APSCommandCreate_JobContextSim  863 //!< sending job context back to ERP: simulation

#define DEF_APSCommandCheckQueues_________  870 //!< inactive, not used in fact: sent as answer to DEF_ERPCommandCheckQueues_________ (inactive, too)

//! tardiness reasoning
#define DEF_APSCommandcreate_ReasonMatResM  880 //!< send incompatibility material/resource reason (partial info)
#define DEF_APSCommandcreate_ReasonMatResR  881 //!< send incompatibility material/resource reason (partial info)
#define DEF_APSCommnadReasonTransferEnd___  882 //!< reason bulk transfer end (only for 'button' request

#define DEF_APSCommandOfflineTest_________  899 //!< for testing communication, testRunner is invoked and messages send to erp as dummy

#define DEF_ERPCommandGetLogFile__________  900 //!< command to send the logfile currently holding to the erp

#define DEF_ERPCommandSimulateOptimization  910

#define DEF_ERPCommandLogStart____________  921 // send logging message to ERP, start of measurement
#define DEF_ERPCommandLogEnd______________  922 // send logging message to ERP, end of measurement

//! commands for ReasonSendingFormat71e
#define DEF_APSCommandcreate_ReasonHead___  930 //!< send reason head information 
#define DEF_APSCommandcreate_Reason_______  931 //!< send reason information 
#define DEF_APSCommandcreate_ReasonAct____  932 //!< send activity information for reason 

// APS server commands are defined in ApsStatus.h

std::string commandToString(long p_lCommand);
