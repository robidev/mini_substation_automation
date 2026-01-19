<?xml version='1.0' encoding='utf-8'?>
<SCL xmlns="http://www.iec.ch/61850/2003/SCL" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2007" revision="B" xsi:schemaLocation="http://www.iec.ch/61850/2003/SCL schema/SCL.xsd" release="4">
  <Header id="proto" nameStructure="IEDName" />
  <Substation name="SS1" desc="2 Incoming 50kV Feeds, 2 Busbars, 2 Power Transformers">
    <VoltageLevel name="VL_50kV" nomFreq="50" numPhases="3">
      <Voltage multiplier="k" unit="V">50</Voltage>
      <Bay name="Bay_Feed1">
        <ConnectivityNode name="CN_FEED1_IN" pathName="SS1/VL_50kV/Bay_Feed1/CN_FEED1_IN" />
        <ConnectivityNode name="CN_FEED1_AFTER_DISCO" pathName="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_DISCO" />
        <ConnectivityNode name="CN_FEED1_AFTER_CT" pathName="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CT" />
        <ConnectivityNode name="CN_FEED1_AFTER_CB" pathName="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CB" />
        <ConnectivityNode name="CN_BUS1" pathName="SS1/VL_50kV/Bay_Feed1/CN_BUS1" />
        <ConnectivityNode name="CN_BUS2" pathName="SS1/VL_50kV/Bay_Feed1/CN_BUS2" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_50kV/Bay_Feed1/CN_GND" />
        <ConductingEquipment name="LINE_F1" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_FEED1_IN" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_FEED1_IN" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="AR_F1" type="SurgeArrester">
          <Terminal name="T1" cNodeName="CN_FEED1_IN" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_GND" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F1" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED1_IN" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_FEED1_AFTER_DISCO" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_DISCO" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_F1" type="CTR">
          <Terminal name="T1" cNodeName="CN_FEED1_AFTER_DISCO" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_DISCO" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_FEED1_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_F1" type="CBR">
          <Terminal name="T1" cNodeName="CN_FEED1_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_FEED1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F1_B1" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F1_B2" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_FEED1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
          <Terminal name="T2" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_Feed1/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed1" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_Feed2">
        <ConnectivityNode name="CN_FEED2_IN" pathName="SS1/VL_50kV/Bay_Feed2/CN_FEED2_IN" />
        <ConnectivityNode name="CN_FEED2_AFTER_DISCO" pathName="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_DISCO" />
        <ConnectivityNode name="CN_FEED2_AFTER_CT" pathName="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CT" />
        <ConnectivityNode name="CN_FEED2_AFTER_CB" pathName="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CB" />
        <ConnectivityNode name="CN_BUS1" pathName="SS1/VL_50kV/Bay_Feed2/CN_BUS1" />
        <ConnectivityNode name="CN_BUS2" pathName="SS1/VL_50kV/Bay_Feed2/CN_BUS2" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_50kV/Bay_Feed2/CN_GND" />
        <ConductingEquipment name="LINE_F2" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_FEED2_IN" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_FEED2_IN" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="AR_F2" type="SurgeArrester">
          <Terminal name="T1" cNodeName="CN_FEED2_IN" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_GND" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F2" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED2_IN" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_FEED2_AFTER_DISCO" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_DISCO" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_F2" type="CTR">
          <Terminal name="T1" cNodeName="CN_FEED2_AFTER_DISCO" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_DISCO" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_FEED2_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_F2" type="CBR">
          <Terminal name="T1" cNodeName="CN_FEED2_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_FEED2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F2_B1" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_F2_B2" type="DIS">
          <Terminal name="T1" cNodeName="CN_FEED2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_FEED2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
          <Terminal name="T2" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_Feed2/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Feed2" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_Busbar1">
        <ConnectivityNode name="CN_BUS1" pathName="SS1/VL_50kV/Bay_Busbar1/CN_BUS1" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_50kV/Bay_Busbar1/CN_GND" />
        <ConductingEquipment name="BUS1" type="BusbarSection">
          <Terminal name="T1" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_Busbar1/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar1" />
          <Terminal name="T2" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_Busbar1/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar1" />
        </ConductingEquipment>
        <ConductingEquipment name="VTR_B1" type="VTR">
          <Terminal name="T1" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_Busbar1/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar1" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_50kV/Bay_Busbar1/CN_GND" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar1" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_Busbar2">
        <ConnectivityNode name="CN_BUS2" pathName="SS1/VL_50kV/Bay_Busbar2/CN_BUS2" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_50kV/Bay_Busbar2/CN_GND" />
        <ConductingEquipment name="BUS2" type="BusbarSection">
          <Terminal name="T1" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_Busbar2/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar2" />
          <Terminal name="T2" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_Busbar2/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar2" />
        </ConductingEquipment>
        <ConductingEquipment name="VTR_B2" type="VTR">
          <Terminal name="T1" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_Busbar2/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar2" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_50kV/Bay_Busbar2/CN_GND" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_Busbar2" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT1">
        <ConnectivityNode name="CN_PT1_HV_IN" pathName="SS1/VL_50kV/Bay_PT1/CN_PT1_HV_IN" />
        <ConnectivityNode name="CN_PT1_AFTER_CT" pathName="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CT" />
        <ConnectivityNode name="CN_PT1_AFTER_CB" pathName="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CB" />
        <ConnectivityNode name="CN_BUS1" pathName="SS1/VL_50kV/Bay_PT1/CN_BUS1" />
        <ConnectivityNode name="CN_BUS2" pathName="SS1/VL_50kV/Bay_PT1/CN_BUS2" />
        <ConnectivityNode name="CN_PT1_LV_IN" pathName="SS1/VL_50kV/Bay_PT1/CN_PT1_LV_IN" />
        <ConnectivityNode name="CN_PT1_MV_BUS" pathName="SS1/VL_50kV/Bay_PT1/CN_PT1_MV_BUS" />
        <PowerTransformer name="PT1" type="PTR">
          <TransformerWinding name="W1" type="PTW">
            <Terminal connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_HV_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" cNodeName="CN_PT1_HV_IN" />
          </TransformerWinding>
          <TransformerWinding name="W2" type="PTW">
            <Terminal connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_IN" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" cNodeName="CN_PT1_LV_IN" />
            <NeutralPoint connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_NEUTRAL" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" cNodeName="CN_PT1_LV_NEUTRAL" />
          </TransformerWinding>
        </PowerTransformer>
        <ConductingEquipment name="CTR_PT1" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT1_HV_IN" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_HV_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
          <Terminal name="T2" cNodeName="CN_PT1_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT1" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT1_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
          <Terminal name="T2" cNodeName="CN_PT1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_PT1_B1" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
          <Terminal name="T2" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_PT1_B2" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_PT1_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
          <Terminal name="T2" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_PT1/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT1" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT2">
        <ConnectivityNode name="CN_PT2_HV_IN" pathName="SS1/VL_50kV/Bay_PT2/CN_PT2_HV_IN" />
        <ConnectivityNode name="CN_PT2_AFTER_CT" pathName="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CT" />
        <ConnectivityNode name="CN_PT2_AFTER_CB" pathName="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CB" />
        <ConnectivityNode name="CN_BUS1" pathName="SS1/VL_50kV/Bay_PT2/CN_BUS1" />
        <ConnectivityNode name="CN_BUS2" pathName="SS1/VL_50kV/Bay_PT2/CN_BUS2" />
        <ConnectivityNode name="CN_PT2_LV_IN" pathName="SS1/VL_50kV/Bay_PT2/CN_PT2_LV_IN" />
        <ConnectivityNode name="CN_PT2_MV_BUS" pathName="SS1/VL_50kV/Bay_PT2/CN_PT2_MV_BUS" />
        <PowerTransformer name="PT2" type="PTR">
          <TransformerWinding name="W1" type="PTW">
            <Terminal connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_HV_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" cNodeName="CN_PT2_HV_IN" />
          </TransformerWinding>
          <TransformerWinding name="W2" type="PTW">
            <Terminal connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_IN" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" cNodeName="CN_PT2_LV_IN" />
            <NeutralPoint connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_NEUTRAL" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" cNodeName="CN_PT2_LV_NEUTRAL" />
          </TransformerWinding>
        </PowerTransformer>
        <ConductingEquipment name="CTR_PT2" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT2_HV_IN" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_HV_IN" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
          <Terminal name="T2" cNodeName="CN_PT2_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT2" type="CBR">
          <LNode lnInst="1" lnClass="XCBR" ldInst="GenericIO" iedName="IED1_XCBR" />
          <Terminal name="T1" cNodeName="CN_PT2_AFTER_CT" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CT" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
          <Terminal name="T2" cNodeName="CN_PT2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_PT2_B1" type="DIS">
          <LNode lnInst="1" lnClass="XSWI" ldInst="GenericIO" iedName="IED1_XCBR" />
          <Terminal name="T1" cNodeName="CN_PT2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
          <Terminal name="T2" cNodeName="CN_BUS1" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_BUS1" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
        </ConductingEquipment>
        <ConductingEquipment name="DIS_PT2_B2" type="DIS">
          <LNode lnInst="2" lnClass="XSWI" ldInst="GenericIO" iedName="IED1_XCBR" />
          <Terminal name="T1" cNodeName="CN_PT2_AFTER_CB" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_PT2_AFTER_CB" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
          <Terminal name="T2" cNodeName="CN_BUS2" connectivityNode="SS1/VL_50kV/Bay_PT2/CN_BUS2" substationName="SS1" voltageLevelName="VL_50kV" bayName="Bay_PT2" />
        </ConductingEquipment>
      </Bay>
    </VoltageLevel>
    <VoltageLevel name="VL_10kV_PT1" nomFreq="50" numPhases="3">
      <Voltage multiplier="k" unit="V">10</Voltage>
      <Bay name="Bay_PT1_MV_Incoming">
        <ConnectivityNode name="CN_PT1_LV_IN" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_IN" />
        <ConnectivityNode name="CN_PT1_AFTER_INCB" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_AFTER_INCB" />
        <ConnectivityNode name="CN_PT1_LV_NEUTRAL" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_NEUTRAL" />
        <ConnectivityNode name="CN_PT1_LV_AFTER_CTR" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_AFTER_CTR" />
        <ConductingEquipment name="DIS_PT1_MV_IN" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_LV_AFTER_CTR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_AFTER_CTR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT1_AFTER_INCB" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_AFTER_INCB" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT1_MV_IN" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT1_AFTER_INCB" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_AFTER_INCB" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT1_MV_IN" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT1_LV_IN" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_IN" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT1_LV_AFTER_CTR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Incoming/CN_PT1_LV_AFTER_CTR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Incoming" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT1_MV_Bus">
        <ConnectivityNode name="CN_PT1_MV_BUS" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_PT1_MV_BUS" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_GND" />
        <ConductingEquipment name="BUS_PT1_MV" type="BusbarSection">
          <Terminal name="T1" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Bus" />
          <Terminal name="T2" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Bus" />
        </ConductingEquipment>
        <ConductingEquipment name="VTR_PT1_MV" type="VTR">
          <Terminal name="T1" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Bus" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Bus/CN_GND" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Bus" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT1_MV_Fdr1">
        <ConnectivityNode name="CN_PT1_FDR1_FROM_BUS" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_FROM_BUS" />
        <ConnectivityNode name="CN_PT1_FDR1_OUT" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_OUT" />
        <ConnectivityNode name="CN_PT1_FDR1_AFTER_CBR" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT1_FDR1" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR1_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT1_FDR1" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR1_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR1_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT1_FDR1" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR1_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT1_FDR1" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT1_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr1/CN_PT1_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr1" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT1_MV_Fdr2">
        <ConnectivityNode name="CN_PT1_FDR2_FROM_BUS" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_FROM_BUS" />
        <ConnectivityNode name="CN_PT1_FDR2_OUT" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_OUT" />
        <ConnectivityNode name="CN_PT1_FDR2_AFTER_CBR" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT1_FDR2" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR2_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT1_FDR2" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR2_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR2_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT1_FDR2" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR2_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT1_FDR2" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT1_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr2/CN_PT1_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr2" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT1_MV_Fdr3">
        <ConnectivityNode name="CN_PT1_FDR3_FROM_BUS" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_FROM_BUS" />
        <ConnectivityNode name="CN_PT1_FDR3_OUT" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_OUT" />
        <ConnectivityNode name="CN_PT1_FDR3_AFTER_CBR" pathName="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT1_FDR3" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT1_MV_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR3_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT1_FDR3" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR3_FROM_BUS" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR3_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT1_FDR3" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT1_FDR3_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT1_FDR3" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT1_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT1_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT1/Bay_PT1_MV_Fdr3/CN_PT1_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT1" bayName="Bay_PT1_MV_Fdr3" />
        </ConductingEquipment>
      </Bay>
    </VoltageLevel>
    <VoltageLevel name="VL_10kV_PT2" nomFreq="50" numPhases="3">
      <Voltage multiplier="k" unit="V">10</Voltage>
      <Bay name="Bay_PT2_MV_Incoming">
        <ConnectivityNode name="CN_PT2_LV_IN" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_IN" />
        <ConnectivityNode name="CN_PT2_AFTER_INCB" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_AFTER_INCB" />
        <ConnectivityNode name="CN_PT2_LV_NEUTRAL" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_NEUTRAL" />
        <ConnectivityNode name="CN_PT2_LV_AFTER_CTR" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_AFTER_CTR" />
        <ConductingEquipment name="DIS_PT2_MV_IN" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT2_LV_AFTER_CTR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_AFTER_CTR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT2_AFTER_INCB" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_AFTER_INCB" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT2_MV_IN" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT2_AFTER_INCB" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_AFTER_INCB" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT2_MV_IN" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT2_LV_IN" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_IN" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
          <Terminal name="T2" cNodeName="CN_PT2_LV_AFTER_CTR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Incoming/CN_PT2_LV_AFTER_CTR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Incoming" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT2_MV_Bus">
        <ConnectivityNode name="CN_PT2_MV_BUS" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_PT2_MV_BUS" />
        <ConnectivityNode name="CN_GND" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_GND" />
        <ConductingEquipment name="BUS_PT2_MV" type="BusbarSection">
          <Terminal name="T1" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Bus" />
          <Terminal name="T2" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Bus" />
        </ConductingEquipment>
        <ConductingEquipment name="VTR_PT2_MV" type="VTR">
          <Terminal name="T1" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Bus" />
          <Terminal name="T2" cNodeName="CN_GND" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Bus/CN_GND" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Bus" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT2_MV_Fdr1">
        <ConnectivityNode name="CN_PT2_FDR1_FROM_BUS" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_FROM_BUS" />
        <ConnectivityNode name="CN_PT2_FDR1_OUT" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_OUT" />
        <ConnectivityNode name="CN_PT2_FDR1_AFTER_CBR" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT2_FDR1" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR1_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT2_FDR1" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR1_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR1_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT2_FDR1" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR1_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT2_FDR1" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT2_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR1_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr1/CN_PT2_FDR1_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr1" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT2_MV_Fdr2">
        <ConnectivityNode name="CN_PT2_FDR2_FROM_BUS" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_FROM_BUS" />
        <ConnectivityNode name="CN_PT2_FDR2_OUT" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_OUT" />
        <ConnectivityNode name="CN_PT2_FDR2_AFTER_CBR" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT2_FDR2" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR2_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT2_FDR2" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR2_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR2_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT2_FDR2" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR2_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT2_FDR2" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT2_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR2_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr2/CN_PT2_FDR2_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr2" />
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay_PT2_MV_Fdr3">
        <ConnectivityNode name="CN_PT2_FDR3_FROM_BUS" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_FROM_BUS" />
        <ConnectivityNode name="CN_PT2_FDR3_OUT" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_OUT" />
        <ConnectivityNode name="CN_PT2_FDR3_AFTER_CBR" pathName="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_AFTER_CBR" />
        <ConductingEquipment name="DIS_PT2_FDR3" type="DIS">
          <Terminal name="T1" cNodeName="CN_PT2_MV_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_MV_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR3_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="CBR_PT2_FDR3" type="CBR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR3_FROM_BUS" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_FROM_BUS" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR3_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="CTR_PT2_FDR3" type="CTR">
          <Terminal name="T1" cNodeName="CN_PT2_FDR3_AFTER_CBR" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_AFTER_CBR" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
        </ConductingEquipment>
        <ConductingEquipment name="FEEDER_PT2_FDR3" type="ACLineSegment">
          <Terminal name="T1" cNodeName="CN_PT2_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
          <Terminal name="T2" cNodeName="CN_PT2_FDR3_OUT" connectivityNode="SS1/VL_10kV_PT2/Bay_PT2_MV_Fdr3/CN_PT2_FDR3_OUT" substationName="SS1" voltageLevelName="VL_10kV_PT2" bayName="Bay_PT2_MV_Fdr3" />
        </ConductingEquipment>
      </Bay>
    </VoltageLevel>
  </Substation>
</SCL>