from flask.json import jsonify
from flask import app, request
import datetime
from models import *
import hashlib,jwt

db.create_all()
db.session.commit()

key='super-secret'

#Api for Admin register
@app.route('/api/adminregister', methods = ['POST'])
def adminRegisterSuccess():
    try:
        data=request.get_json()
        password=data['password']
        admin_check= Admin_Login.query.filter_by(email=data['email']).first()
        if not admin_check:
            entry = Admin_Login(email=data['email'],password=password)
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success':True,'message':'Admin Registration Successful'}), 201
        else:
            return jsonify({'success':False,'message':'Admin Already Existed for this email'}), 404 
    except:
        return jsonify({"success":False, "message":"not recieved JSON data"}), 400

# Api for Patient Register
@app.route('/api/patientregister', methods=['POST'])
def patientRegisterSuccess():
    try:    
        data=request.get_json()
        password=data['password']
        hashpass= str(hashlib.md5(bytes(str(password),encoding ='utf-8')).hexdigest())
        patient_check= Patient_details.query.filter_by(email=data['email']).first()
        if not patient_check:
            entry = Patient_details(name=data['name'],age=data['age'],email=data['email'],password=hashpass,contact=data['contact'],gender=data['gender'],address=data['address'])
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success':True,'message':'Registration Successful'})
        else:
            return jsonify({'success':False,'message':'Patient Already Existed for this email'}), 404 
    except Exception as e:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400


# Api for Doctor Register
@app.route('/api/doctorregister', methods=['POST'])
def doctorRegisterSuccess():
    try:    
        data=request.get_json()
        password=data['password']
        hashpass= str(hashlib.md5(bytes(str(password),encoding ='utf-8')).hexdigest())
        doctor_check= doctor_details.query.filter_by(email=data['email']).first()
        if not doctor_check:
            entry = doctor_details(name=data['name'],category = data['category'],email=data['email'],password=hashpass)
            db.session.add(entry)
            db.session.commit()
            return jsonify({'success':True,'message':'Registration Successful'})
        else:
            return jsonify({'success':False,'message':'Doctor Already Existed for this email'}), 404 
    except Exception as e:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400

# Api for Admin Login
@app.route('/api/adminlogin',methods=['POST'])
def adminLoginSuccess():
    try:
        all_data=request.get_json()
        result = Admin_Login.query.filter_by(email=all_data['email'], password=all_data['password']).first()
        if result:
            payload={"email":all_data['email'],"password":all_data['password'] }
            value = jwt.encode(payload, key)
            return jsonify({'success':True,'token':value})
        else:
            return jsonify({'success':False,'message':'Wrong Password'}), 404
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}), 400

# Api for Patient Login
@app.route('/api/patientlogin', methods=['POST'])
def patientLoginSucess():
    try:
        all_data=request.get_json()
        hashedPassword = str(hashlib.md5(bytes(str(all_data['password']),encoding='utf-8')).hexdigest())
        result = Patient_details.query.filter_by(email=all_data['email'], password=hashedPassword).first()
        if result:
            payload={"email":all_data['email'],"password":hashedPassword }
            value = jwt.encode(payload, key)
            patient_info={'id':result.id,'name':result.name,'age':result.age,'email':result.email,'contact':result.contact,'gender':result.gender,'address':result.address}
            return jsonify({'success':True,'token':value, 'patient_info':patient_info})
        else:
            return jsonify({'success':False,'message':'invalid email/Password'}), 404
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400


# Api for Doctor Login
@app.route('/api/doctorlogin', methods=['POST'])
def doctorLoginSucess():
    try:
        all_data=request.get_json()
        hashedPassword = str(hashlib.md5(bytes(str(all_data['password']),encoding='utf-8')).hexdigest())
        result = doctor_details.query.filter_by(email=all_data['email'], password=hashedPassword).first()
        if result:
            payload={"email":all_data['email'],"password":hashedPassword }
            value = jwt.encode(payload, key)
            doctor_info={'name':result.name,'category':result.category,'email':result.email}
            return jsonify({'success':True,'token':value, 'doctor_info':doctor_info})
        else:
            return jsonify({'success':False,'message':'invalid email/Password'}), 404
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400      


#1. Medication Summary
@app.route('/api/ips/medicationsummary/getallmedicationstatementsforpatient',methods=['GET'])
def getallmedicationstatements():
    try:
        #patient verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        patient = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if patient:
            output={}

            #check medication_summary
            medication_summary=Medication_summary.query.filter_by(patient_id=patient.id).first()

            if medication_summary:
                output['global_exclusion_of_medication_use']=medication_summary.global_exclusion_of_medication_use
                output['absence_of_info_statement']=medication_summary.absence_of_info_statement
                output['absence_of_info_protocol_last_updated']=medication_summary.absence_of_info_protocol_last_updated
            
                medication_statements=Medication_statement.query.filter_by(patient_id=patient.id).all()
                medicationstatements=[]

                for medication_statement in medication_statements:
                    obj={}
                    
                    obj['order_id']=medication_statement.order_id
                    obj['medication_item']=medication_statement.medication_item

                    medicationstatements.append(obj)
                
                output['medication_statements']=medicationstatements
            return jsonify({"success":True, "medication_summary":output}),200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


@app.route('/api/ips/medicationsummary/getallmedicationstatementsfordoctor/<int:patient_id>',methods=['GET'])
def getallmedicationstatementsfordoctor(patient_id):
    try:
        #doctor verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        doctor = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if doctor:
            #patient verification
            patient = Patient_details.query.filter_by(id=patient_id).first()
            if patient:
                output={}
                #check medication_summary
                medication_summary=Medication_summary.query.filter_by(patient_id=patient.id).first()

                if medication_summary:
                    output['global_exclusion_of_medication_use']=medication_summary.global_exclusion_of_medication_use
                    output['absence_of_info_statement']=medication_summary.absence_of_info_statement
                    output['absence_of_info_protocol_last_updated']=medication_summary.absence_of_info_protocol_last_updated
                
                    medication_statements=Medication_statement.query.filter_by(patient_id=patient.id).all()
                    medicationstatements=[]

                    for medication_statement in medication_statements:
                        obj={}
                        
                        obj['order_id']=medication_statement.order_id
                        obj['medication_item']=medication_statement.medication_item

                        medicationstatements.append(obj)
                    
                    output['medication_statements']=medicationstatements
                return jsonify({"success":True, "medication_summary":output}),200

            else:
                return jsonify({'success':False, 'message': 'Invalid Patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


@app.route('/api/ips/medicationsummary/getmedicationstatementforpatient/<int:Order_Id>',methods=['GET'])
def getmedicationstatement(Order_Id):
    try:
        #patient authentication
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        patient = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()

        if patient:
            result=db.session.query(Medication_statement).filter(Order_Id==Medication_statement.order_id,patient.id==Medication_statement.patient_id).first()
            if result:

                out={}

                obj={}
                obj['order_id']=result.order_id
                obj['patient_id']=result.patient_id
                l=obj

                obj={}
                obj['medication_item']=result.medication_item
                obj['medication_name']=result.medication_name
                obj['medication_form']=result.medication_form
                obj['strength(concentration)']=result.strength_concentration
                obj['medication_category']=result.medication_category
                obj['medication_strength_numerator']=result.medication_strength_numerator
                obj['medication_strength_numerator_unit']=result.medication_strength_numerator_unit
                obj['medication_strength_denominator']=result.medication_strength_denominator
                obj['medication_strength_denominator_unit']=result.medication_strength_denominator_unit
                obj['unit_of_presentation']=result.unit_of_presentation
                obj['strength']=result.strength
                obj['manufacturer']=result.manufacturer
                obj['batch_id']=result.batch_id
                obj['expiry']=result.expiry
                obj['amount']=result.amount
                obj['amount_unit']=result.amount_unit
                obj['alternate_amount']=result.alternate_amount
                obj['alternate_amount_unit']=result.alternate_amount_unit
                obj['role']=result.role
                obj['description']=result.description
                m=obj
                
                obj={}
                obj['dose_amount']=result.dose_amount
                obj['dose_unit']=result.dose_unit
                obj['dose_formula']=result.dose_formula
                obj['dose_description']=result.dose_description
                obj['frequency_lower']=result.dose_frequency_lower
                obj['frequency_lower_rate']=result.dose_frequency_lower_rate
                obj['frequency_higher']=result.dose_frequency_higher
                obj['frequency_higher_rate']=result.dose_frequency_higher_rate
                obj['interval']=result.dose_interval
                obj['specific_time']=result.dose_specific_time
                obj['specific_time_lower']=result.dose_specific_time_lower
                obj['specific_time_upper']=result.dose_specific_time_upper
                obj['timing_description']=result.timing_description
                obj['exact_timing_critical']=result.dose_exact_timing_critical
                obj['as_required']=result.as_required
                obj['as_required_criterion']=result.as_required_criterion
                obj['event_name']=result.dose_event_name
                obj['time_offset']=result.dose_time_offset
                obj['on']=result.dose_on
                obj['off']=result.dose_off
                obj['repetetions']=result.dose_repetetions
                n=obj

                obj={}
                obj['route']=result.route
                obj['body_site']=result.body_site
                o=obj

                obj={}
                obj['repetetion_interval']=result.time_repetetion_interval
                obj['frequency_lower']=result.time_frequency_lower
                obj['frequency_lower_rate']=result.time_frequency_lower_rate
                obj['frequency_higher']=result.time_frequency_higher
                obj['frequency_higher_rate']=result.time_frequency_higher_rate
                obj['specific_date']=result.time_specific_date
                obj['specific_date_lower']=result.time_specific_date_lower
                obj['specific_date_upper']=result.time_specific_date_upper
                obj['specific_day_of_week']=result.time_specific_day_of_week
                obj['specific_day_of_month']=result.time_specific_day_of_month
                obj['timing_description']=result.timing_description
                obj['event_name']=result.time_event_name
                obj['event_time_offset']=result.time_event_time_offset
                obj['on']=result.timing_on
                obj['off']=result.timing_off
                obj['repetetions']=result.timing_repetetions
                p=obj
                
                out={'medication_statement':l,"medication":m,"dosage":n,"administration_details":o,"timing_non-daily":p}
                return jsonify({"success":True, "data":out}),200

            else:
                return jsonify({'success':False,'message':'not authorised'}), 401
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


@app.route('/api/ips/medicationsummary/getmedicationstatementfordoctor/<int:Order_Id>',methods=['GET'])
def getmedicationstatementfordoctor(Order_Id):
    try:
        #doctor verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        doctor = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if doctor:
            result=db.session.query(Medication_statement).filter(Order_Id==Medication_statement.order_id).first()
            
            if result:
                out={}

                obj={}
                obj['order_id']=result.order_id
                obj['patient_id']=result.patient_id
                l=obj

                obj={}
                obj['medication_item']=result.medication_item
                obj['medication_name']=result.medication_name
                obj['medication_form']=result.medication_form
                obj['strength(concentration)']=result.strength_concentration
                obj['medication_category']=result.medication_category
                obj['medication_strength_numerator']=result.medication_strength_numerator
                obj['medication_strength_numerator_unit']=result.medication_strength_numerator_unit
                obj['medication_strength_denominator']=result.medication_strength_denominator
                obj['medication_strength_denominator_unit']=result.medication_strength_denominator_unit
                obj['unit_of_presentation']=result.unit_of_presentation
                obj['strength']=result.strength
                obj['manufacturer']=result.manufacturer
                obj['batch_id']=result.batch_id
                obj['expiry']=result.expiry
                obj['amount']=result.amount
                obj['amount_unit']=result.amount_unit
                obj['alternate_amount']=result.alternate_amount
                obj['alternate_amount_unit']=result.alternate_amount_unit
                obj['role']=result.role
                obj['description']=result.description
                m=obj
                
                obj={}
                obj['dose_amount']=result.dose_amount
                obj['dose_unit']=result.dose_unit
                obj['dose_formula']=result.dose_formula
                obj['dose_description']=result.dose_description
                obj['frequency_lower']=result.dose_frequency_lower
                obj['frequency_lower_rate']=result.dose_frequency_lower_rate
                obj['frequency_higher']=result.dose_frequency_higher
                obj['frequency_higher_rate']=result.dose_frequency_higher_rate
                obj['interval']=result.dose_interval
                obj['specific_time']=result.dose_specific_time
                obj['specific_time_lower']=result.dose_specific_time_lower
                obj['specific_time_upper']=result.dose_specific_time_upper
                obj['timing_description']=result.timing_description
                obj['exact_timing_critical']=result.dose_exact_timing_critical
                obj['as_required']=result.as_required
                obj['as_required_criterion']=result.as_required_criterion
                obj['event_name']=result.dose_event_name
                obj['time_offset']=result.dose_time_offset
                obj['on']=result.dose_on
                obj['off']=result.dose_off
                obj['repetetions']=result.dose_repetetions
                n=obj

                obj={}            
                obj['route']=result.route
                obj['body_site']=result.body_site
                o=obj

                obj={}
                obj['repetetion_interval']=result.time_repetetion_interval
                obj['frequency_lower']=result.time_frequency_lower
                obj['frequency_lower_rate']=result.time_frequency_lower_rate
                obj['frequency_higher']=result.time_frequency_higher
                obj['frequency_higher_rate']=result.time_frequency_higher_rate
                obj['specific_date']=result.time_specific_date
                obj['specific_date_lower']=result.time_specific_date_lower
                obj['specific_date_upper']=result.time_specific_date_upper
                obj['specific_day_of_week']=result.time_specific_day_of_week
                obj['specific_day_of_month']=result.time_specific_day_of_month
                obj['timing_description']=result.timing_description
                obj['event_name']=result.time_event_name
                obj['event_time_offset']=result.time_event_time_offset
                obj['on']=result.timing_on
                obj['off']=result.timing_off
                obj['repetetions']=result.timing_repetetions
                p=obj
               
                out={'medication_statement':l,"medication":m,"dosage":n,"administration_details":o,"timing_non-daily":p}
                return jsonify({"success":True, "data":out}),200

            else:
                return jsonify({'success':False,'message':'Invalid Order id'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400



@app.route('/api/ips/medicationsummary/addmedicationstatement',methods=['POST'])
def addmedicationstatement():
    try:
        #admin verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Admin_Login.query.filter_by(email=value['email'], password=value['password']).first()

        if res:
            data=request.get_json()
            #patient verification
            result1 = Patient_details.query.filter_by(id = data['patient_id']).first()

            if result1:
                result2 = Medication_summary.query.filter_by(patient_id = data['patient_id']).first()
                if result2:
                    result2.global_exclusion_of_adverse_reactions = data['global_exclusion_of_adverse_reactions']
                    result2.absence_of_information_statement = data['absence_of_information_statement']
                    result2.absence_of_information_protocol_last_updated = data['absence_of_information_protocol_last_updated']
                else:
                    entry = Medication_summary(patient_id=data['patient_id'],global_exclusion_of_medication_use=data['global_exclusion_of_adverse_reactions'],absence_of_info_statement=data['absence_of_information_statement'],absence_of_info_protocol_last_updated=data['absence_of_information_protocol_last_updated'])
                    db.session.add(entry)
                
                entry_medication = Medication_statement(
                    patient_id=data['patient_id'],
                    medication_item=data['medication_item'],
                    medication_name=data['medication_name'],
                    medication_form=data['medication_form'],
                    strength_concentration=data['strength(concentration)'],
                    medication_category=data['medication_category'],
                    medication_strength_numerator=data['medication_strength_numerator'],
                    medication_strength_numerator_unit=data['medication_strength_numerator_unit'],
                    medication_strength_denominator=data['medication_strength_denominator'],
                    medication_strength_denominator_unit=data['medication_strength_denominator_unit'],
                    unit_of_presentation=data['unit_of_presentation'],
                    strength=data['strength'],
                    manufacturer=data['manufacturer'],
                    batch_id=data['batch_id'],
                    expiry=data['expiry'],
                    amount=data['amount'],
                    amount_unit=data['amount_unit'],
                    alternate_amount=data['alternate_amount'],
                    alternate_amount_unit=data['alternate_amount_unit'],
                    role=data['role'],
                    description=data['description'],

                    dose_amount=data['dose_amount'],
                    dose_unit=data['dose_unit'],
                    dose_formula=data['dose_formula'],
                    dose_description=data['dose_description'],
                    dose_frequency_lower=data['dose_frequency_lower'],
                    dose_frequency_lower_rate=data['dose_frequency_lower_rate'],
                    dose_frequency_higher=data['dose_frequency_higher'],
                    dose_frequency_higher_rate=data['dose_frequency_higher_rate'],
                    dose_interval=data['dose_interval'],
                    dose_specific_time=data['dose_specific_time'],
                    dose_specific_time_lower=data['dose_specific_time_lower'],
                    dose_specific_time_upper=data['dose_specific_time_upper'],
                    dose_timing_description=data['dose_timing_description'],
                    dose_exact_timing_critical=data['dose_exact_timing_critical'],
                    as_required=data['as_required'],
                    as_required_criterion=data['as_required_criterion'],
                    dose_event_name=data['dose_event_name'],
                    dose_time_offset=data['dose_time_offset'],
                    dose_on=data['dose_on'],
                    dose_off=data['dose_off'],
                    dose_repetetions=data['dose_repetetions'],
                    route=data['route'],
                    body_site=data['body_site'],
            
                    time_repetetion_interval=data['time_repetetion_interval'],
                    time_frequency_lower=data['time_frequency_lower'],
                    time_frequency_lower_rate=data['time_frequency_lower_rate'],
                    time_frequency_higher=data['time_frequency_higher'],
                    time_frequency_higher_rate=data['time_frequency_higher_rate'],
                    time_specific_date=data['time_specific_date'],
                    time_specific_date_lower=data['time_specific_date_lower'],
                    time_specific_date_upper=data['time_specific_date_upper'],
                    time_specific_day_of_week=data['time_specific_day_of_week'],
                    time_specific_day_of_month=data['time_specific_day_of_month'],
                    timing_description=data['timing_description'],
                    time_event_name=data['time_event_name'],
                    time_event_time_offset=data['time_event_time_offset'],
                    timing_on=data['timing_on'],
                    timing_off=data['timing_off'],
                    timing_repetetions=data['timing_repetetions']
                )
                    
                db.session.add(entry_medication)

                db.session.commit() 
                return jsonify({'success':True,'message':'item added successfully'}),201

            else:
                return jsonify({'success':False, 'message':'Invalid Patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not Admin'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


#2. PRESCRIPTION
# ADD prescription POST 
@app.route('/api/addPrescription', methods=['POST'])
def addPrescription():
    try:
        #doctor verification
        token = request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]

        docResult = doctor_details.query.filter_by(email=email,password=password).first()
        if docResult:
            docId = docResult.id
            data = request.get_json()
            patId = data['patient_id']
            #patient verification
            result = Patient_details.query.filter_by(id = patId).first()
            if result:
               
                current_date =datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                entry = Prescription(doctorId=docId,patientId=patId,dateWritten=current_date)
                db.session.add(entry)

                for medOrd in data['medOrders']:
                    entry_med_ord = Medication_Order(
                    dateWritten = current_date,
                    patientId=patId,
                    doctorId=docId,
                    medicationItem = medOrd['medicationItem'],
                    route = medOrd['route'],
                    dosageInstruction = medOrd['dosageInstruction'],
                    maximumAmount = medOrd['maximumAmount'],
                    maximumAmountDoseUnit = medOrd['maximumAmountDoseUnit'],
                    allowedPeriod = medOrd['allowedPeriod'],
                    overrideReason = medOrd['overrideReason'],
                    additionalInstructions = medOrd['additionalInstructions'],
                    reasons = medOrd['reasons'],
                    status=medOrd['status'],
                    dateDiscontinued = medOrd['dateDiscontinued'],
                    numOfRepeatsAllowed = medOrd['numOfRepeatsAllowed'],
                    validityPeriod = medOrd['validityPeriod'],
                    dispenseInstrution =  medOrd['dispenseInstrution'],
                    dispenseAmountDescription = medOrd['dispenseAmountDescription'],
                    dispenseAmount = medOrd['dispenseAmount'],
                    dispenseAmountUnit = medOrd['dispenseAmountUnit'],
                    comment = medOrd['comment'],
                    dose_unit   =  medOrd['dose_unit'],
                    dose_frequency = medOrd['dose_frequency'],
                    dose_timing   = medOrd['dose_timing'],
                    dose_duration = medOrd['dose_duration'],

                    repetition_interval = medOrd['repetition_interval'],
                    Specific_date = medOrd['Specific_date'],
                    specific_day_of_week = medOrd['specific_day_of_week'],
                    Specific_day_of_month = medOrd['Specific_day_of_month'],
                    specific_Event = medOrd['specific_Event'],

                    substance_name = medOrd['substance_name'],
                    form = medOrd['form'],
                    strength = medOrd['strength'],
                    strengthUnit =medOrd['strengthUnit'],
                    diluentAmount = medOrd['diluentAmount'],
                    diluentunit = medOrd['diluentunit'],
                    description = medOrd['description']
                    )
                    db.session.add(entry_med_ord)

                db.session.commit()
                return jsonify({'success':True,'message':'Prescription Created Successfully'}),201
            else:
                return jsonify({'success':False,'message':'Invalid Patient'}),404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a doctor'}),401

    except Exception as e :
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400 

        
# GET API for prescription
@app.route('/api/getAllPrescriptionsForPatient', methods=['GET'])
def getAllPrescriptionsForPatient():
    try:
        #patient verification
        token = request.headers['token']    
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        patRes = Patient_details.query.filter_by(email=email,password=password).first()

        if patRes:
            patId = patRes.id
            prescriptions = Prescription.query.filter_by(patientId=patId).all()
            result = []
            for prescription in prescriptions:
                obj = {}
                docName = doctor_details.query.filter_by(id = prescription.doctorId).first().name
                obj['doctorName'] = docName
                obj['prescriptionId'] = prescription.id
                obj['date_written']=prescription.dateWritten
                result.append(obj)
            return jsonify({'success':True,'allPrescriptions':result}),200        
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}),401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400 


# For doctor

@app.route('/api/getAllPrescriptionsForDoctor', methods=['GET'])
def getAllPrescriptionsForDoctor():

    try:
        #doctor verification
        token = request.headers['token'] 
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        
        docRes = doctor_details.query.filter_by(email=email,password=password).first()
        if docRes:
            docId = docRes.id
            prescriptions = Prescription.query.filter_by(doctorId=docId).all()
            result = []
            for prescription in prescriptions:
                obj = {}
                patName = Patient_details.query.filter_by(id = prescription.patientId).first().name
                obj['patientName'] = patName
                obj['prescriptionId'] = prescription.id
                obj['date_written']=prescription.dateWritten
                result.append(obj)
            return jsonify({'success':True,'allPrescriptions':result}),200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a doctor'}),401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400 




# getPrescription by ID
@app.route('/api/getPrescriptionByIdForDoctor/<int:presId>', methods=['GET'])
def getPrescriptionByIdForDoct(presId):
    try:
        #doctor Verification
        token = request.headers['token'] 
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        docRes = doctor_details.query.filter_by(email=email,password=password).first()
        
        if docRes:
            docverfify = Prescription.query.filter_by(id=presId, doctorId =docRes.id).first()
            if docverfify:
                result = Medication_Order.query.filter_by(doctorId=docRes.id,patientId=docverfify.patientId,dateWritten=docverfify.dateWritten).all()
                output = []
                for item in result:
                    detail = {}
                    detail['medicationItem'] = item.medicationItem
                    detail['medId'] = item.medId
                    detail['date_written']=item.dateWritten
                    detail['patient_id']=item.patientId

                    output.append(detail)
                return jsonify({'success':True,'Prescription':output}),200
            else:
                return jsonify({'success':False,'message':'Not Authorised'}),401
        else:
            return jsonify({'success':False,'message':'Not Authorised, Not a Doctor'}),401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400 

# getprescription by id
@app.route('/api/getPrescriptionByIdForPatient/<int:presId>', methods=['GET'])
def getPrescriptionByIdForPat(presId):
    try:
        token = request.headers['token']    #doctor token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]

        patRes = Patient_details.query.filter_by(email=email,password=password).first()
        
        if patRes:
            patverfify = Prescription.query.filter_by(id=presId, patientId =patRes.id).first()
            if patverfify:
                result = Medication_Order.query.filter_by(doctorId=patverfify.doctorId,patientId=patRes.id,dateWritten=patverfify.dateWritten).all()
                output = []
                for item in result:
                    detail = {}
                    detail['medicationItem'] = item.medicationItem
                    detail['medId'] = item.medId
                    detail['date_written']=item.dateWritten
                    detail['patient_id']=item.patientId
                    output.append(detail)
                return jsonify({'success':True,'Prescription':output}),200
            else:
                return jsonify({'success':False,'message':'Not Authorised'}),401
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}),401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400

#getmedication order by id API
@app.route('/api/getMedicationOrderByIdForDoctor/<int:medId>', methods=['GET'])
def getMedicationOrderByIdForDoctor(medId):
    try:
        token = request.headers['token']    #doctor token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]

        docRes = doctor_details.query.filter_by(email=email,password=password).first()
        if docRes:
            result = Medication_Order.query.filter_by(medId = medId).first()
            pres_id = Prescription.query.filter_by(patientId=result.patientId,doctorId=result.doctorId,dateWritten=result.dateWritten).first().id
            docverify =Prescription.query.filter_by(id = pres_id,doctorId=docRes.id).first()
            if docverify:
                if result:
                    output = {}
                    output['medicationItem'] = result.medicationItem
                    output['route'] =  result.route
                    output['dosageInstruction'] = result.dosageInstruction
                    output['maximumAmount'] = result.maximumAmount 
                    output['maximumAmountDoseUnit'] =result.maximumAmountDoseUnit
                    output['allowedPeriod'] =  result.allowedPeriod
                    output['overrideReason'] = result.overrideReason
                    output['additionalInstructions'] =result.additionalInstructions
                    output['reasons'] =result.reasons
                    output['status'] =result.status
                    output['dateDiscontinued']=result.dateDiscontinued
                    output['dateWritten']=result.dateWritten
                    output['numOfRepeatsAllowed']=result.numOfRepeatsAllowed
                    output['validityPeriod']=result.validityPeriod
                    output['dispenseInstrution']=result.dispenseInstrution
                    output['dispenseAmountDescription']=result.dispenseAmountDescription
                    output['dispenseAmount']=result.dispenseAmount
                    output['dispenseAmountUnit']=result.dispenseAmountUnit
                    output['comment']=result.comment
                    output['dose_unit']=result.dose_unit
                    output['dose_frequency']=result.dose_frequency
                    output['dose_timing']=result.dose_timing
                    output['dose_duration']=result.dose_duration
                    output['repetition_interval']=result.repetition_interval
                    output['Specific_date']=result.Specific_date
                    output['specific_day_of_week']=result.specific_day_of_week
                    output['Specific_day_of_month']=result.Specific_day_of_month
                    output['specific_Event']=result.specific_Event
                    output['substance_name']=result.substance_name
                    output['form']=result.form
                    output['strength']=result.strength
                    output['strengthUnit']=result.strengthUnit
                    output['diluentAmount']=result.diluentAmount
                    output['diluentunit']=result.diluentunit
                    output['description']=result.description
                    return jsonify(output),200
                else:
                    return jsonify({'success':False,'message':'Invalid Med Id'}),404
            else:
                return jsonify({'success':False,'message':'Not Authorised'}),401
        else:
            return jsonify({'success':False,'message':'Not Authorised, Not a Doctor'}),401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON/Token data'}),400 
    


#getmedication order by id API
@app.route('/api/getMedicationOrderByIdForPatient/<int:medId>', methods=['GET'])
def getMedicationOrderByIdForPatient(medId):
    try:
        token = request.headers['token']    #doctor token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]

        patRes = Patient_details.query.filter_by(email=email,password=password).first()
        if patRes:
            result = Medication_Order.query.filter_by(medId = medId).first()
            pres_id = Prescription.query.filter_by(patientId=result.patientId,doctorId=result.doctorId,dateWritten=result.dateWritten).first().id
            patverify =Prescription.query.filter_by(id = pres_id,patientId=patRes.id).first()
            if patverify:

                if result:
                    output = {}
                    output['medicationItem'] = result.medicationItem
                    output['route'] =  result.route
                    output['dosageInstruction'] = result.dosageInstruction
                    output['maximumAmount'] = result.maximumAmount 
                    output['maximumAmountDoseUnit'] =result.maximumAmountDoseUnit
                    output['allowedPeriod'] =  result.allowedPeriod
                    output['overrideReason'] = result.overrideReason
                    output['additionalInstructions'] =result.additionalInstructions
                    output['reasons'] =result.reasons
                    output['status'] =result.status
                    output['dateDiscontinued']=result.dateDiscontinued
                    output['dateWritten']=result.dateWritten
                    output['numOfRepeatsAllowed']=result.numOfRepeatsAllowed
                    output['validityPeriod']=result.validityPeriod
                    output['dispenseInstrution']=result.dispenseInstrution
                    output['dispenseAmountDescription']=result.dispenseAmountDescription
                    output['dispenseAmount']=result.dispenseAmount
                    output['dispenseAmountUnit']=result.dispenseAmountUnit
                    output['comment']=result.comment
                    output['dose_unit']=result.dose_unit
                    output['dose_frequency']=result.dose_frequency
                    output['dose_timing']=result.dose_timing
                    output['dose_duration']=result.dose_duration
                    output['repetition_interval']=result.repetition_interval
                    output['Specific_date']=result.Specific_date
                    output['specific_day_of_week']=result.specific_day_of_week
                    output['Specific_day_of_month']=result.Specific_day_of_month
                    output['specific_Event']=result.specific_Event
                    output['substance_name']=result.substance_name
                    output['form']=result.form
                    output['strength']=result.strength
                    output['strengthUnit']=result.strengthUnit
                    output['diluentAmount']=result.diluentAmount
                    output['diluentunit']=result.diluentunit
                    output['description']=result.description
                    return jsonify(output),200
                else:
                    return jsonify({'success':False,'message':'Invalid Med Id'}),404
            else:
                return jsonify({'success':False,'message':'Not Authorised'}),401
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}),401

    except Exception as e:
        return jsonify({'success':False,'message':'not recieved JSON/Token data', "error":str(e)}),400 


#3. Pregnancy
# API for POST PREGNANCY 
@app.route('/api/addPregnancyDetails',methods=['POST'])
def addPregnancyDetails():
    try:
        #admin Verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:
                entry = Pregnancy(
                    patient_uid=data['patient_id'],
                    pregnancy_status = data['pregnancy_status'],
                    pregnancy_outcome = data['pregnancy_outcome'],
                    estimated_date_of_delivery_by_date_of_conseption = data['estimated_date_of_delivery_by_date_of_conseption'],
                    estimated_date_of_delivery_by_cycle = data['estimated_date_of_delivery_by_cycle'],
                    estimated_date_of_delivery_by_ultrasound = data['estimated_date_of_delivery_by_ultrasound'],
                    agreed_date = data['agreed_date'],
                    protocol_last_updated = data['protocol_last_updated'],
                    exclusion_of_pregnancy_statement = data['exclusion_of_pregnancy_statement']
                )
                db.session.add(entry)
                db.session.commit()
                return jsonify({'success':True,'message':'pregnancy details Added successfully'}),201

            else:
                return jsonify({'success':True,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


# Api for Get past history of PAtient BY PAtient Id
@app.route('/api/getPregnancyRecordForPatient',methods=['GET'])
def getPregnancyRecordForPatient():
    try:
        #patient verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            result = db.session.query(Pregnancy).filter(Pregnancy.patient_uid==res.id).all()
            output=[]     
            for value in result:
                pat = {}
                pat['patient_id']=value.patient_uid
                pat['pregnancy_status']=value.pregnancy_status
                pat['pregnancy_outcome']=value.pregnancy_outcome
                pat['estimated_date_of_delivery_by_date_of_conseption']=value.estimated_date_of_delivery_by_date_of_conseption
                pat['estimated_date_of_delivery_by_cycle']=value.estimated_date_of_delivery_by_cycle
                pat['estimated_date_of_delivery_by_ultrasound']=value.estimated_date_of_delivery_by_ultrasound
                pat['agreed_date']=value.agreed_date
                pat['protocol_last_updated']=value.protocol_last_updated
                pat['exclusion_of_pregnancy_statement']=value.exclusion_of_pregnancy_statement
                output.append(pat)
                    
            return jsonify({'success':True,"history":output}),200 
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404     
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400      
    

# Api for Get past history of PAtient BY Doctor 
@app.route('/api/getPregnancyRecordForDoctor/<int:patient_id>',methods=['GET'])
def getPregnancyRecordForDoctor(patient_id):
    try:
        #doctor verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        doctor = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if doctor:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            if patient:
                result = db.session.query(Pregnancy).filter(Pregnancy.patient_uid==patient_id).all()
                output=[]     
                for value in result:
                    pat = {}
                    pat['patient_id']=value.patient_uid
                    pat['pregnancy_status']=value.pregnancy_status
                    pat['pregnancy_outcome']=value.pregnancy_outcome
                    pat['estimated_date_of_delivery_by_date_of_conseption']=value.estimated_date_of_delivery_by_date_of_conseption
                    pat['estimated_date_of_delivery_by_cycle']=value.estimated_date_of_delivery_by_cycle
                    pat['estimated_date_of_delivery_by_ultrasound']=value.estimated_date_of_delivery_by_ultrasound
                    pat['agreed_date']=value.agreed_date
                    pat['protocol_last_updated']=value.protocol_last_updated
                    pat['exclusion_of_pregnancy_statement']=value.exclusion_of_pregnancy_statement
                    output.append(pat)
                return jsonify({'success':True,"history":output}),200

            else:
                return jsonify({'success':False, 'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'not authorised, not a doctor'}), 401       
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400      


#4. History of Proceedures
@app.route('/api/addHistoryOfProcedure',methods=['POST'])
def historyOfProcedure():
    try:
        #Admin verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:
                # Check for pre existing proceedures
                procedures = db.session.query(history_of_procedures).filter(history_of_procedures.patient_uid==data['patient_id']).first()
                
                if not procedures:
                    entry = history_of_procedures(
                        patient_uid=data['patient_id'],
                        absence_of_info_absence_statement = data['absence_of_info_absence_statement'],
                        absence_of_info_protocol_last_updated = data['absence_of_info_protocol_last_updated'],
                        global_exclusion_of_procedures = data['global_exclusion_of_procedures']
                    )
                    db.session.add(entry)
                else:
                    procedures.absence_of_info_absence_statement = data['absence_of_info_absence_statement'],
                    procedures.absence_of_info_protocol_last_updated = data['absence_of_info_protocol_last_updated'],
                    procedures.global_exclusion_of_procedures = data['global_exclusion_of_procedures']

                entry1=Procedure(
                    patient_uid=data['patient_id'],
                    procedure_name = data['procedure_name'],
                    body_site = data['body_site']
                )
                db.session.add(entry1)
                db.session.commit()
                return jsonify({'success':True,'message':'history of procedure added successfully'}),201
            else:
                return jsonify({'success':False, 'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400



# GET API FOR Historyofprocedure for Doctor
@app.route('/api/getHistoryOfProcedureforDoctor/<int:patient_id>',methods=['GET'])
def getHistoryOfProcedureForDoctor(patient_id):
    try:
        #doctor verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        doctor_check= doctor_details.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if doctor_check:
            patient_uid = patient_id
            #patient verification
            patient = Patient_details.query.filter_by(id=patient_uid).first()
            if patient:
                pat = {}
                result1 = db.session.query(history_of_procedures).filter(history_of_procedures.patient_uid==patient_uid).first()
                
                if result1:
                    pat['patient_id']=result1.patient_uid
                    pat['absence_of_info_absence_statement']=result1.absence_of_info_absence_statement
                    pat['absence_of_info_protocol_last_updated']=result1.absence_of_info_protocol_last_updated
                    pat['global_exclusion_of_procedures']=result1.global_exclusion_of_procedures

                    result2 = db.session.query(Procedure).filter(Procedure.patient_uid==patient_uid).all()   
                    output=[]

                    for value in result2:  
                        obj={}  
                        obj['procedure_name']=value.procedure_name
                        obj['body_site']=value.body_site
                        output.append(obj)

                    pat['procedures']=output
                        
                return jsonify({'success':True,"history_of_procedure":pat}),200

            else:
                return jsonify({'success':False, 'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a doctor'}), 401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400     


# GET API FOR Historyofprocedure for Patient
@app.route('/api/getHistoryOfProcedureforPatient',methods=['GET'])
def getHistoryOfProcedureForPatient():
    try:
        #patient verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        patient_check= Patient_details.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if patient_check:
            patient_uid = patient_check.id
            pat = {}
            result1 = db.session.query(history_of_procedures).filter(history_of_procedures.patient_uid==patient_uid).first()
            
            if result1:
                pat['patient_id']=result1.patient_uid
                pat['absence_of_info_absence_statement']=result1.absence_of_info_absence_statement
                pat['absence_of_info_protocol_last_updated']=result1.absence_of_info_protocol_last_updated
                pat['global_exclusion_of_procedures']=result1.global_exclusion_of_procedures

                result2 = db.session.query(Procedure).filter(Procedure.patient_uid==patient_uid).all()   
                output=[]

                for value in result2:  
                    obj={}  
                    obj['procedure_name']=value.procedure_name
                    obj['body_site']=value.body_site
                    output.append(obj)

                pat['procedures']=output

            return jsonify({'success':True,"history_of_procedure":pat}),200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400


#5. Immunization
# POST for add immunization by Admin
@app.route('/api/addImmunizations',methods=['POST'])
def addImmunizations():
    try:
        #admin verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()
            
            if patient:
                immunizations = db.session.query(Immunizations).filter(Immunizations.patient_uid==data['patient_id']).first()
                if not immunizations:
                    entry = Immunizations(
                        patient_uid=data['patient_id'],
                        absence_of_info_absence_statement = data['absence_of_info_absence_statement'],
                        absence_of_info_protocol_last_updated = data['absence_of_info_protocol_last_updated']
                    )
                    db.session.add(entry)
                else:
                    immunizations.absence_of_info_absence_statement = data['absence_of_info_absence_statement'],
                    immunizations.absence_of_info_protocol_last_updated = data['absence_of_info_protocol_last_updated']

                entry1=Immunization(
                    patient_uid=data['patient_id'],
                    immunization_item=data['immunization_item'],
                    administration_details_route = data['administration_details_route'],
                    administration_details_target_site = data['administration_details_target_site'],
                    sequence_number = data['sequence_number']
                )
                db.session.add(entry1)
                db.session.commit()
                return jsonify({'success':True,'message':'Immunizations added successfully'}),201

            else:
                return jsonify({'success':False, 'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400
    

# GET API FOR Immunizations for Patient
@app.route('/api/getImmunizationsForPatient',methods=['GET'])
def getImmunizationsForPatient():
    try:
        #patient verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        patient_check= Patient_details.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if patient_check:
            patient_uid = patient_check.id

            pat = {}
            result1 = db.session.query(Immunizations).filter(Immunizations.patient_uid==patient_uid).first()
            
            if result1:
                pat['patient_uid']=result1.patient_uid
                pat['absence_of_info_absence_statement']=result1.absence_of_info_absence_statement
                pat['absence_of_info_protocol_last_updated']=result1.absence_of_info_protocol_last_updated
                
                result2 = db.session.query(Immunization).filter(Immunization.patient_uid==patient_uid).all()
                output=[]

                for value in result2:  
                    obj={}  
                    obj['patient_id']=value.patient_uid
                    obj['immunization_item']=value.immunization_item
                    obj['administration_details_route']=value.administration_details_route
                    obj['administration_details_target_site']=value.administration_details_target_site
                    obj['sequence_number']=value.sequence_number
                    output.append(obj)

                pat['immunizations']=output  
            return jsonify({'success':True,"immunization":pat}),200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400

# GET API FOR Immunizations for Doctor
@app.route('/api/getImmunizationsForDoctor/<int:patient_id>',methods=['GET'])
def getImmunizationsForDoctor(patient_id):

    try:
        #doctor verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        doctor_check= doctor_details.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if doctor_check:
            patient_uid = patient_id
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_uid).first()

            if patient:

                pat = {}
                result1 = db.session.query(Immunizations).filter(Immunizations.patient_uid==patient_uid).first()
                
                if result1:
                    pat['patient_uid']=result1.patient_uid
                    pat['absence_of_info_absence_statement']=result1.absence_of_info_absence_statement
                    pat['absence_of_info_protocol_last_updated']=result1.absence_of_info_protocol_last_updated
                    
                    result2 = db.session.query(Immunization).filter(Immunization.patient_uid==patient_uid).all()
                    output=[]

                    for value in result2:  
                        obj={}  
                        obj['patient_id']=value.patient_uid
                        obj['immunization_item']=value.immunization_item
                        obj['administration_details_route']=value.administration_details_route
                        obj['administration_details_target_site']=value.administration_details_target_site
                        obj['sequence_number']=value.sequence_number
                        output.append(obj)

                    pat['immunizations']=output 

                return jsonify({'success':True,"immunization":pat}),200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a Doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400


#6. Medical Devices
# API for POST Medical Device
@app.route('/api/addMedicalDevice',methods=['POST'])
def addMedicalDevice():
    try:
        #Admin verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:
                entry = Medical_devices(
                    patient_uid=data['patient_id'],
                    device_name = data['device_name'],
                    body_site = data['body_site'],
                    type = data['type'],
                    description = data['description'],
                    UDI = data['UDI'],
                    manufacturer = data['manufacturer'],
                    date_of_manufacture = data['date_of_manufacture'],
                    serial_number = data['serial_number'],
                    catalogue_number = data['catalogue_number'],
                    model_number = data['model_number'],
                    batch_number = data['batch_number'],
                    software_version = data['software_version'],
                    date_of_expiry = data['date_of_expiry'],
                    other_identifier = data['other_identifier'],
                    comment = data['comment']
                )
                db.session.add(entry)
                db.session.commit()
                return jsonify({'success':True,'message':'Medical Devices Added successfully'}),201
            
            else:
                return jsonify({'success':False, 'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not Admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


# Api for Get MedicalDevice For Patient 
@app.route('/api/getMedicalDeviceForPatient',methods=['GET'])
def getMedicalDeviceForPatient():
    try:
        #patient verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            result = db.session.query(Medical_devices).filter(Medical_devices.patient_uid==res.id).all()
            output=[]  

            for value in result:
                pat = {}
                pat['patient_id']=value.patient_uid
                pat['device_name']=value.device_name
                pat['body_site']=value.body_site
                pat['type']=value.type
                pat['description']=value.description
                pat['UDI']=value.UDI
                pat['manufacturer']=value.manufacturer
                pat['date_of_manufacture']=value.date_of_manufacture
                pat['serial_number']=value.serial_number
                pat['catalogue_number']=value.catalogue_number
                pat['model_number']=value.model_number
                pat['batch_number']=value.batch_number
                pat['software_version']=value.software_version
                pat['date_of_expiry']=value.date_of_expiry
                pat['other_identifier']=value.other_identifier
                pat['comment']=value.comment
                output.append(pat)  
    
            return jsonify({'success':True,"medical_devices":output}),200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404       
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400      


# Api for Get MedicalDevice For Doctor 
@app.route('/api/getMedicalDeviceForDoctor/<int:patient_id>',methods=['GET'])
def getMedicalDeviceForDoctor(patient_id):
    try:
        #doctor verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:

            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            if patient:
                result = db.session.query(Medical_devices).filter(Medical_devices.patient_uid==patient_id).all()
                output=[]   

                for value in result:
                    pat = {}
                    pat['patient_id']=value.patient_uid
                    pat['device_name']=value.device_name
                    pat['body_site']=value.body_site
                    pat['type']=value.type
                    pat['description']=value.description
                    pat['UDI']=value.UDI
                    pat['manufacturer']=value.manufacturer
                    pat['date_of_manufacture']=value.date_of_manufacture
                    pat['serial_number']=value.serial_number
                    pat['catalogue_number']=value.catalogue_number
                    pat['model_number']=value.model_number
                    pat['batch_number']=value.batch_number
                    pat['software_version']=value.software_version
                    pat['date_of_expiry']=value.date_of_expiry
                    pat['other_identifier']=value.other_identifier
                    pat['comment']=value.comment
                    output.append(pat)
                return jsonify({'success':True,"medical_devices":output}),200
            else:
                return jsonify({'success':False, 'message': 'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'not authorised, not a doctor'}), 401       
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400      

#prashast

#7. Allergies
#add allergy
@app.route('/api/add_allergies_and_intolerances', methods=['POST'])
def add_allergies_and_intolerances():
    try:
        #Admin verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        admin = Admin_Login.query.filter_by(email=value['email'], password=value['password']).first()
        
        if admin:
            data = request.get_json()
            #patient verification
            result = Patient_details.query.filter_by(id = data['patient_id']).first()
            if result:
                result_allergies = allergies_and_intolerances.query.filter_by(patient_id = data['patient_id']).first()
                if result_allergies:
                    result_allergies.global_exclusion_of_adverse_reactions = data['global_exclusion_of_adverse_reactions']
                    result_allergies.absence_of_information_statement = data['absence_of_information_statement']
                    result_allergies.absence_of_information_protocol_last_updated = data['absence_of_information_protocol_last_updated']
                else:
                    entry_allergies = allergies_and_intolerances(patient_id = data['patient_id'], global_exclusion_of_adverse_reactions = data['global_exclusion_of_adverse_reactions'], absence_of_information_statement = data['absence_of_information_statement'], absence_of_information_protocol_last_updated = data['absence_of_information_protocol_last_updated'])
                    db.session.add(entry_allergies)
                entry_allergy = Allergy(patient_id=data['patient_id'], substance=data['substance'], verification_status=data['verification_status'], critically=data['critically'], type=data['type'], comment=data['comment'], reaction_manifestation = data['reaction_manifestation'], onset = data['onset'], severity = data['severity'], protocol_last_updated = data['protocol_last_updated'])
                db.session.add(entry_allergy)
                db.session.commit()
                return jsonify({'success':True, 'message':'data added'}), 201
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not an admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 

#get all allergies
    #for doctor
@app.route('/api/get_all_allergies_and_intolerances_for_doctor/<int:patient_id>', methods=['GET'])
def getallAllergiesForDoctor(patient_id):
    try:
        #doctor verification
        token = request.headers['token'] 
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        doctor = doctor_details.query.filter_by(email=email,password=password).first()

        if doctor:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            if patient:
                output = {}
                result = allergies_and_intolerances.query.filter_by(patient_id = patient_id).first()
                if result:
                    
                    output['global_exclusion_of_adverse_reactions'] = result.global_exclusion_of_adverse_reactions
                    output['absence_of_information_statement'] = result.absence_of_information_statement
                    output['absence_of_information_protocol_last_updated'] = result.absence_of_information_protocol_last_updated
                    
                    allergy_list = []
                    allergies = Allergy.query.filter_by(patient_id = patient_id).all()
                    for allergy in allergies:
                        obj = {}
                        obj['substance']= allergy.substance
                        obj['allergy_id']= allergy.id
                        allergy_list.append(obj)
                    output['allergy_list'] = allergy_list

                return jsonify({'all_allergies_and_intolerances':output}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get all allergies
    #for patient
@app.route('/api/get_all_allergies_and_intolerances_for_patient', methods=['GET'])
def getallAllergiesForPatient():
    try:
        #patient verification
        token = request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]

        patient = Patient_details.query.filter_by(email=email,password=password).first()
        if patient:
            output = {}
            result = allergies_and_intolerances.query.filter_by(patient_id = patient.id).first()
            
            if result:
                output['global_exclusion_of_adverse_reactions'] = result.global_exclusion_of_adverse_reactions
                output['absence_of_information_statement'] = result.absence_of_information_statement
                output['absence_of_information_protocol_last_updated'] = result.absence_of_information_protocol_last_updated
                
                allergy_list = []
                allergies = Allergy.query.filter_by(patient_id = patient.id).all()

                for allergy in allergies:
                    obj = {}
                    obj['substance']= allergy.substance
                    obj['allergy_id']= allergy.id
                    allergy_list.append(obj)

                output['allergy_list'] = allergy_list
            
            return jsonify({'success':True,'all_allergies_and_intolerances':output}), 200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get allergy by id
    #for doctor
@app.route('/api/get_allergy_by_id_for_doctor/<int:allergy_id>', methods = ['GET'])
def getAllergyByIdForDoctor(allergy_id):
    try:
        #doctor verification
        token = request.headers['token']   
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        doctor = doctor_details.query.filter_by(email=email,password=password).first()
        
        if doctor:
            output = {}
            result = Allergy.query.filter_by(id = allergy_id).first()

            if result:
                output['substance'] = result.substance
                output['verification_status'] = result.verification_status
                output['critically'] = result.critically
                output['type'] = result.type
                output['comment'] = result.comment
                output['reaction_manifestation'] = result.reaction_manifestation
                output['onset'] = result.onset
                output['severity'] = result.severity
                output['protocol_last_updated'] = result.protocol_last_updated

            return jsonify({'success':True,'allergy':output}), 200

        else:
            return jsonify({'success':False, "message":"Not authorised, not a doctor"}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get allergy by id
    #for patient
@app.route('/api/get_allergy_by_id_for_patient/<int:allergy_id>', methods = ['GET'])
def getAllergyByIdForPatient(allergy_id):
    try:
        #patient verification
        token = request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        patient = Patient_details.query.filter_by(email=email,password=password).first()
        
        if patient:
            result = Allergy.query.filter_by(id = allergy_id, patient_id=patient.id).first()
            if result:
                output = {}
                output['substance'] = result.substance
                output['verification_status'] = result.verification_status
                output['critically'] = result.critically
                output['type'] = result.type
                output['comment'] = result.comment
                output['reaction_manifestation'] = result.reaction_manifestation
                output['onset'] = result.onset
                output['severity'] = result.severity
                output['protocol_last_updated'] = result.protocol_last_updated

                return jsonify({'success':True,'allergy':output}), 200
            else:
                return jsonify({'success':False, "message":"Not Authorised"}), 401
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#8. Vital signs
#add/update vital signs
@app.route('/api/add_vital_signs', methods=['POST'])
def add_vital_signs():
    try:
        #Admin verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        admin = Admin_Login.query.filter_by(email=value['email'], password=value['password']).first()
       
        if admin:
            data = request.get_json()
            #patient verification
            result = Patient_details.query.filter_by(id = data['patient_id']).first()
            if result:
                result_vitals = vital_signs.query.filter_by(patient_id= data['patient_id']).first()
                if result_vitals:
                    result_vitals.body_weight = data['body_weight']
                    result_vitals.body_weight_unit = data['body_weight_unit']
                    result_vitals.height = data['height']
                    result_vitals.height_unit = data['height_unit']
                    result_vitals.respiration_rate = data['respiration_rate']
                    result_vitals.pulse_rate = data['pulse_rate']
                    result_vitals.body_temperature = data['body_temperature']
                    result_vitals.body_temperature_unit = data['body_temperature_unit']
                    result_vitals.head_circumference = data['head_circumference']
                    result_vitals.head_circumference_unit = data['head_circumference_unit']
                    result_vitals.pulse_oximetry = data['pulse_oximetry']
                    result_vitals.body_mass_index = data['body_mass_index']
                    result_vitals.body_mass_index_unit = data['body_mass_index_unit']
                    result_vitals.blood_pressure_systolic = data['blood_pressure_systolic']
                    result_vitals.blood_pressure_diastolic = data['blood_pressure_diastolic']
                else:
                    entry = vital_signs(patient_id = data['patient_id'], body_weight = data['body_weight'], body_weight_unit = data['body_weight_unit'], height = data['height'],height_unit = data['height_unit'],respiration_rate = data['respiration_rate'],pulse_rate = data['pulse_rate'],body_temperature = data['body_temperature'],body_temperature_unit = data['body_temperature_unit'],head_circumference = data['head_circumference'],head_circumference_unit = data['head_circumference_unit'],pulse_oximetry = data['pulse_oximetry'],body_mass_index = data['body_mass_index'],body_mass_index_unit = data['body_mass_index_unit'],blood_pressure_systolic = data['blood_pressure_systolic'],blood_pressure_diastolic = data['blood_pressure_diastolic'])
                    db.session.add(entry)
                db.session.commit()
                return jsonify({'success':True, 'message':'data added'}), 201
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not an admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 

#get vital signs
    #for doctor
@app.route('/api/get_vital_signs_for_doctor/<int:patient_id>', methods=['GET'])
def get_vital_signs_for_doctor(patient_id):
    try:
        #doctor verification
        token = request.headers['token']    
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        doctor = doctor_details.query.filter_by(email=email,password=password).first()

        if doctor:
            patient = Patient_details.query.filter_by(id = patient_id).first()

            if patient:
                obj = {}
                result_vitals = vital_signs.query.filter_by(patient_id = patient.id).first()

                if result_vitals:
                    obj['body_weight']=result_vitals.body_weight 
                    obj['body_weight_unit']=result_vitals.body_weight_unit 
                    obj['height']=result_vitals.height
                    obj['height_unit']=result_vitals.height_unit 
                    obj['respiration_rate']=result_vitals.respiration_rate 
                    obj['pulse_rate']=result_vitals.pulse_rate 
                    obj['body_temperature']=result_vitals.body_temperature 
                    obj['body_temperature_unit']=result_vitals.body_temperature_unit 
                    obj['head_circumference']=result_vitals.head_circumference 
                    obj['head_circumference_unit']=result_vitals.head_circumference_unit 
                    obj['pulse_oximetry']=result_vitals.pulse_oximetry
                    obj['body_mass_index']=result_vitals.body_mass_index 
                    obj['body_mass_index_unit']=result_vitals.body_mass_index_unit 
                    obj['blood_pressure_systolic']=result_vitals.blood_pressure_systolic 
                    obj['blood_pressure_diastolic']=result_vitals.blood_pressure_diastolic
                return jsonify({'success':True,'data':obj}), 200
                
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get vital signs
    #for patient
@app.route('/api/get_vital_signs_for_patient', methods=['GET'])
def get_vital_signs_for_patient():
    try:
        token = request.headers['token']    #patient token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        patient = Patient_details.query.filter_by(email=email,password=password).first()

        if patient:
            obj = {}
            result_vitals = vital_signs.query.filter_by(patient_id = patient.id).first()

            if result_vitals:
                obj['body_weight']=result_vitals.body_weight 
                obj['body_weight_unit']=result_vitals.body_weight_unit 
                obj['height']=result_vitals.height
                obj['height_unit']=result_vitals.height_unit 
                obj['respiration_rate']=result_vitals.respiration_rate 
                obj['pulse_rate']=result_vitals.pulse_rate 
                obj['body_temperature']=result_vitals.body_temperature 
                obj['body_temperature_unit']=result_vitals.body_temperature_unit 
                obj['head_circumference']=result_vitals.head_circumference 
                obj['head_circumference_unit']=result_vitals.head_circumference_unit 
                obj['pulse_oximetry']=result_vitals.pulse_oximetry
                obj['body_mass_index']=result_vitals.body_mass_index 
                obj['body_mass_index_unit']=result_vitals.body_mass_index_unit 
                obj['blood_pressure_systolic']=result_vitals.blood_pressure_systolic 
                obj['blood_pressure_diastolic']=result_vitals.blood_pressure_diastolic
            return jsonify({'success':True,'data':obj}), 200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 

#9. Dignostics
#add dignosis
@app.route('/api/add_dignostics_results', methods=['POST'])
def add_dignostics_results():
    try:
        #Admin verification
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        admin = Admin_Login.query.filter_by(email=value['email'], password=value['password']).first()
        if admin:
            data = request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()
            if patient:
                #diagnostic_lab_test_result
                entry = dignostic_test_result(
                    patient_id = data['patient_id'],
                    lab_test_name = data['lab_test_name'],
                    specimen_type = data['specimen_type'],
                    specimen_method = data['specimen_method'],
                    specimen_bodysite = data['specimen_bodysite'],
                    diagnostic_service_category = data['diagnostic_service_category'],
                    laboratory_analyte_result_analyte_name = data['laboratory_analyte_result_analyte_name'],
                    interpretation = data['interpretation'],
                    multimedia_source_resource_name = data['multimedia_source_resource_name'],
                    multimedia_source_content = data['multimedia_source_content'],
                    imaging_test_name = data['imaging_test_name'],
                    modality = data['modality'],
                    anatomical_site = data['anatomical_site'],
                    imaging_finding_name = data['imaging_finding_name'],
                    anatomical_location = data['anatomical_location'],
                    presence = data['presence'],
                    description = data['description'],
                    comparison_to_previous = data['comparison_to_previous'],
                    comment = data['comment'],
                    comparison_with_previous = data['comparison_with_previous'],
                    conclusion = data['conclusion'],
                    imaging_differential_diagnosis = data['imaging_differential_diagnosis'],
                    imaging_diagnosis = data['imaging_diagnosis'],
                    multimedia_resource_name = data['multimedia_resource_name'],
                    multimedia_content = data['multimedia_content'],
                    technique = data['technique'],
                    imaging_quality = data['imaging_quality'],
                    examination_requester_order_identifier = data['examination_requester_order_identifier'],
                    examination_requested_name = data['examination_requested_name'],
                    examination_receiver_order_identifier = data['examination_receiver_order_identifier'],
                    dicom_study_identifier = data['dicom_study_identifier'],
                    examination_report_identifier = data['examination_report_identifier'],
                    image_identifier = data['image_identifier'],
                    dicom_series_identifier = data['dicom_series_identifier'],
                    view = data['view'],
                    position = data['position'],
                    image_datetime = data['image_datetime'],
                    image = data['image']
                )
                db.session.add(entry)
                db.session.commit()
                return jsonify({'success':True, 'message':'data added'}), 201    
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not an Admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get all dignosis
    #for doctor
@app.route('/api/get_dignosis_results_for_doctor/<int:patient_id>', methods=['GET'])
def getDignosisResultsForDoctor(patient_id):
    try:
        #doctor verification
        token = request.headers['token']   
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        doctor = doctor_details.query.filter_by(email=email,password=password).first()

        if doctor:
            patient = Patient_details.query.filter_by(id = patient_id).first()

            if patient:
                results = dignostic_test_result.query.filter_by(patient_id=patient.id).all()
                output =[]

                for result in results:
                    obj ={}
                    obj['dignostic_id']= result.id
                    obj['lab_test_name'] = result.lab_test_name
                    obj['imaging_test_name'] = result.imaging_test_name
                    output.append(obj)

                return jsonify({'success':True,'dignostic_test_result':output}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


#get all dignosis
    #for patient
@app.route('/api/get_dignosis_results_for_patient', methods=['GET'])
def getDignosisResultsForPatient():
    try:
        #patient verification
        token = request.headers['token']   
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        patient = Patient_details.query.filter_by(email=email,password=password).first()

        if patient:
            results = dignostic_test_result.query.filter_by(patient_id=patient.id).all()
            output =[]

            for result in results:
                obj ={}
                obj['dignosis_id']= result.id
                obj['lab_test_name'] = result.lab_test_name
                obj['imaging_test_name'] = result.imaging_test_name
                output.append(obj)
            
            return jsonify({'success':True,'dignostic_test_result':output}), 200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401

    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data/token'}),400 


#get dignostics_by_id
    #for doctor
@app.route('/api/get_dognostics_by_id_for_doctor/<int:dignostic_id>', methods=['GET'])
def getDignosticsByIdForDoctor(dignostic_id):
    try:
        #doctor verification
        token = request.headers['token']    
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        doctor = doctor_details.query.filter_by(email=email,password=password).first()

        if doctor:
            result = dignostic_test_result.query.filter_by(id = dignostic_id).first()

            if result:
                obj = {}
                obj['lab_test_name'] = result.lab_test_name
                obj['specimen_type'] = result.specimen_type
                obj['specimen_method'] = result.specimen_method
                obj['specimen_bodysite'] = result.specimen_bodysite
                obj['diagnostic_service_category'] = result.diagnostic_service_category
                obj['laboratory_analyte_result_analyte_name'] = result.laboratory_analyte_result_analyte_name
                obj['interpretation'] = result.interpretation
                obj['multimedia_source_resource_name'] = result.multimedia_source_resource_name
                obj['multimedia_source_content'] = result.multimedia_source_content
                obj['imaging_test_name'] = result.imaging_test_name
                obj['modality'] = result.modality
                obj['anatomical_site'] = result.anatomical_site
                obj['imaging_finding_name'] = result.imaging_finding_name
                obj['anatomical_location'] = result.anatomical_location
                obj['presence'] = result.presence
                obj['description'] = result.description
                obj['comparison_to_previous'] = result.comparison_to_previous
                obj['comment'] = result.comment
                obj['comparison_with_previous'] = result.comparison_with_previous
                obj['conclusion'] = result.conclusion
                obj['imaging_differential_diagnosis'] = result.imaging_differential_diagnosis
                obj['imaging_diagnosis'] = result.imaging_diagnosis
                obj['multimedia_resource_name'] = result.multimedia_resource_name
                obj['multimedia_content'] = result.multimedia_content
                obj['technique'] = result.technique
                obj['imaging_quality'] = result.imaging_quality
                obj['examination_requester_order_identifier'] = result.examination_requester_order_identifier
                obj['examination_requested_name'] = result.examination_requested_name
                obj['examination_receiver_order_identifier'] = result.examination_receiver_order_identifier
                obj['dicom_study_identifier'] = result.dicom_study_identifier
                obj['examination_report_identifier'] = result.examination_report_identifier
                obj['image_identifier'] = result.image_identifier
                obj['dicom_series_identifier'] = result.dicom_series_identifier
                obj['view'] = result.view
                obj['position'] = result.position
                obj['image_datetime'] = result.image_datetime
                obj['image'] = result.image
                return jsonify({'success':True,'dignostic':obj}), 200

            else:
                return jsonify({'success':False,'message':'Wrong dignostic id'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data/token'}),400 


#get dignostics_by_id
    #for patient
@app.route('/api/get_dognostics_by_id_for_patient/<int:dignostic_id>', methods=['GET'])
def getDignosticsByIdForPatient(dignostic_id):
    try:
        #patient verification
        token = request.headers['token']    
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        patient = Patient_details.query.filter_by(email=email,password=password).first()

        if patient:
            result = dignostic_test_result.query.filter_by(id = dignostic_id, patient_id = patient.id).first()
            
            if result:
                obj = {}
                obj['lab_test_name'] = result.lab_test_name
                obj['specimen_type'] = result.specimen_type
                obj['specimen_method'] = result.specimen_method
                obj['specimen_bodysite'] = result.specimen_bodysite
                obj['diagnostic_service_category'] = result.diagnostic_service_category
                obj['laboratory_analyte_result_analyte_name'] = result.laboratory_analyte_result_analyte_name
                obj['interpretation'] = result.interpretation
                obj['multimedia_source_resource_name'] = result.multimedia_source_resource_name
                obj['multimedia_source_content'] = result.multimedia_source_content
                obj['imaging_test_name'] = result.imaging_test_name
                obj['modality'] = result.modality
                obj['anatomical_site'] = result.anatomical_site
                obj['imaging_finding_name'] = result.imaging_finding_name
                obj['anatomical_location'] = result.anatomical_location
                obj['presence'] = result.presence
                obj['description'] = result.description
                obj['comparison_to_previous'] = result.comparison_to_previous
                obj['comment'] = result.comment
                obj['comparison_with_previous'] = result.comparison_with_previous
                obj['conclusion'] = result.conclusion
                obj['imaging_differential_diagnosis'] = result.imaging_differential_diagnosis
                obj['imaging_diagnosis'] = result.imaging_diagnosis
                obj['multimedia_resource_name'] = result.multimedia_resource_name
                obj['multimedia_content'] = result.multimedia_content
                obj['technique'] = result.technique
                obj['imaging_quality'] = result.imaging_quality
                obj['examination_requester_order_identifier'] = result.examination_requester_order_identifier
                obj['examination_requested_name'] = result.examination_requested_name
                obj['examination_receiver_order_identifier'] = result.examination_receiver_order_identifier
                obj['dicom_study_identifier'] = result.dicom_study_identifier
                obj['examination_report_identifier'] = result.examination_report_identifier
                obj['image_identifier'] = result.image_identifier
                obj['dicom_series_identifier'] = result.dicom_series_identifier
                obj['view'] = result.view
                obj['position'] = result.position
                obj['image_datetime'] = result.image_datetime
                obj['image'] = result.image
                return jsonify({'success':True,'dignostic':obj}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised'}), 401
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data/token'}),400 

# GET PATIENT
    # for doctor
@app.route('/api/getPatientForDoctor', methods=['GET'])
def getPatientForDoctor():
    try:
        token = request.headers['token']    #doctor token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        
        doctor = doctor_details.query.filter_by(email=email,password=password).first()
        if doctor:
            pat_email=request.args.get('email').strip("'").strip('"')
            patient = Patient_details.query.filter_by(email = pat_email).first()
            if patient:
                obj = {}
                obj['id'] = patient.id
                obj['name'] = patient.name
                obj['age'] = patient.age
                obj['email'] = patient.email
                obj['contact'] = patient.contact
                obj['gender'] = patient.gender
                obj['address'] = patient.address
                return jsonify({"success":True,"patient":obj}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data/token'}),400 
        

# GET PATIENT
    # for admin
@app.route('/api/getPatientForAdmin', methods=['GET'])
def getPatientForAdmin():
    try:
        token = request.headers['token']    #admin token
        value = jwt.decode(token, options={"verify_signature": False})
        email = value["email"]
        password = value["password"]
        
        admin = Admin_Login.query.filter_by(email=email,password=password).first()
        if admin:
            pat_email=request.args.get('email').strip("'").strip('"')
            patient = Patient_details.query.filter_by(email = pat_email).first()
            if patient:
                obj = {}
                obj['id'] = patient.id
                obj['name'] = patient.name
                obj['age'] = patient.age
                obj['email'] = patient.email
                obj['contact'] = patient.contact
                obj['gender'] = patient.gender
                obj['address'] = patient.address
                return jsonify({"success":True,"patient":obj}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not an admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data/token'}),400 
        
        
#Twinkle

#10. Past History of patient
# Api for Get past history of Patient BY Patient Id
@app.route('/api/getpasthistoryofpatient',methods=['GET'])
def getPastHistoryPatient():
    try:
        #patient verification
        token=request.headers['token'] 
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            result = db.session.query(Past_history_of_illnesses).filter(Past_history_of_illnesses.patient_id==res.id).all()
            output=[] 
            c = 1   

            for value in result:
                pat = {}
                pat['id'] = c
                c += 1
                pat['patient_id']=value.patient_id
                pat['problem_name']=value.problem_name
                pat['body_site']=value.body_site
                pat['datetime_of_onset']=value.datetime_of_onset
                pat['severity']=value.severity
                pat['date_of_abatebent']=value.date_of_abatebent
                pat['active_or_inactive']=value.active_or_inactive
                pat['resolution_phase']=value.resolution_phase
                pat['remission_status']=value.remission_status
                pat['occurrence']=value.occurrence
                pat['diagnostic_certainity']=value.diagnostic_certainity
                pat['protocol_last_updated']=value.protocol_last_updated
                output.append(pat)
                
            return jsonify({"success":True,"history":output}),200
        
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401       
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 

# Api for Get past history of Patient BY Doctor
@app.route('/api/getpasthistoryofpatientfordoctor/<int:patient_id>',methods=['GET'])
def getPastHistoryDoctor(patient_id):
    try:
        token=request.headers['token'] #patient token
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()

            if patient: 
                result = db.session.query(Past_history_of_illnesses).filter(Past_history_of_illnesses.patient_id==patient_id).all()
                output=[]     

                for value in result:
                    pat = {}
                    pat['patient_id']=value.patient_id
                    pat['problem_name']=value.problem_name
                    pat['body_site']=value.body_site
                    pat['datetime_of_onset']=value.datetime_of_onset
                    pat['severity']=value.severity
                    pat['date_of_abatebent']=value.date_of_abatebent
                    pat['active_or_inactive']=value.active_or_inactive
                    pat['resolution_phase']=value.resolution_phase
                    pat['remission_status']=value.remission_status
                    pat['occurrence']=value.occurrence
                    pat['diagnostic_certainity']=value.diagnostic_certainity
                    pat['protocol_last_updated']=value.protocol_last_updated
                    output.append(pat)
                        
                return jsonify({"success":True,"history":output}),200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404 
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401      
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400              


# Api for get past history of patient by patient id and past history id
   
# Api for create past history of patient
@app.route('/api/createpasthistoryofpatient',methods=['POST'])
def createPastHistoryOfPatient():
    try:
        #Admin Verification
        token = request.headers['token'] 
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:
                entry = Past_history_of_illnesses(
                        patient_id=data['patient_id'],
                        problem_name=data['problem_name'],
                        body_site=data['body_site'],
                        datetime_of_onset=data['datetime_of_onset'],
                        severity=data['severity'],
                        date_of_abatebent=data['date_of_abatebent'],
                        active_or_inactive=data['active_or_inactive'],
                        resolution_phase=data['resolution_phase'],
                        remission_status=data['remission_status'],
                        occurrence=data['occurrence'],
                        diagnostic_certainity=data['diagnostic_certainity'],
                        protocol_last_updated=data['protocol_last_updated'])

                db.session.add(entry)
                db.session.commit()
                return jsonify({'success':True,'message':'history added successfully'}),201

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not an admin'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


#11. problem List

# Api gor Get problem List of Patient
@app.route('/api/getproblemlistbypatient',methods=['GET'])
def getProblemListByPatient():
    try:
        token=request.headers['token']   #Patient Token
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            output = {}
            result1 = db.session.query(Problem_list).filter(Problem_list.patient_id==res.id).first()
            
            if result1:  
                output['patient_id']=result1.patient_id
                output['global_exclusion_of_adverse_reactions']=result1.global_exclusion_of_adverse_reactions
                output['absence_of_information_statement']=result1.absence_of_information_statement
                output['absence_of_information_protocol_last_updated']=result1.absence_of_information_protocol_last_updated
                pat =[]
                result2 = db.session.query(Problem).filter(Problem.patient_id==res.id).all()   
                c = 1
                for value in result2:
                    obj={}
                    obj['id']= c
                    c += 1
                    obj['patient_id']=value.patient_id
                    obj['problem_name']=value.problem_name
                    obj['body_site']=value.body_site
                    obj['datetime_of_onset']=value.datetime_of_onset
                    obj['severity']=value.severity
                    obj['date_of_abatebent']=value.date_of_abatebent
                    obj['active_or_inactive']=value.active_or_inactive
                    obj['resolution_phase']=value.resolution_phase
                    obj['remission_status']=value.resolution_phase
                    obj['occurrence']=value.occurrence
                    obj['diagnostic_certainity']=value.diagnostic_certainity
                    obj['protocol_last_updated']=value.protocol_last_updated
                    pat.append(obj)
                output['problem list'] = pat    

            return jsonify({"success":True,"history":output}), 200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401 
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400     

# Api for Get problem List of Patient by doctor
@app.route('/api/getproblemlistbydoctor/<int:patient_id>',methods=['GET'])
def getProblemListByDoctor(patient_id):
    try:
        token=request.headers['token']   #Doctor Token
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            
            if patient:
                output = {}
                result1 = db.session.query(Problem_list).filter(Problem_list.patient_id==patient_id).first()
                
                if result1:     
                    output['patient_id']=result1.patient_id
                    output['global_exclusion_of_adverse_reactions']=result1.global_exclusion_of_adverse_reactions
                    output['absence_of_information_statement']=result1.absence_of_information_statement
                    output['absence_of_information_protocol_last_updated']=result1.absence_of_information_protocol_last_updated
                    pat =[]
                    result2 = db.session.query(Problem).filter(Problem.patient_id==res.id).all()
                    c = 1

                    for value in result2:
                        obj={}
                        obj['id']= c
                        c += 1
                        obj['patient_id']=value.patient_id
                        obj['problem_name']=value.problem_name
                        obj['body_site']=value.body_site
                        obj['datetime_of_onset']=value.datetime_of_onset
                        obj['severity']=value.severity
                        obj['date_of_abatebent']=value.date_of_abatebent
                        obj['active_or_inactive']=value.active_or_inactive
                        obj['resolution_phase']=value.resolution_phase
                        obj['remission_status']=value.resolution_phase
                        obj['occurrence']=value.occurrence
                        obj['diagnostic_certainity']=value.diagnostic_certainity
                        obj['protocol_last_updated']=value.protocol_last_updated
                        pat.append(obj)
                    output['problem list'] = pat  

                return jsonify({"success":True,"history":output}), 200
            
            else:
                return jsonify({'success':True, "message":'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not a doctor'}), 401 
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400


# Api for Create problem List
@app.route('/api/addproblemlist',methods=['POST'])
def addproblemList():
    try:
        #admin verification
        token = request.headers['token']  #Admin Token
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()
            if patient:
                problem_list = Problem_list.query.filter_by(patient_id = patient.id).first()
                if problem_list:
                    problem_list.global_exclusion_of_adverse_reactions=data['global_exclusion_of_adverse_reactions']
                    problem_list.absence_of_information_statement=data['absence_of_information_statement']
                    problem_list.absence_of_information_protocol_last_updated=data['absence_of_information_protocol_last_updated']
                else:
                    entry = Problem_list(
                        patient_id=data['patient_id'],
                        global_exclusion_of_adverse_reactions=data['global_exclusion_of_adverse_reactions'],
                        absence_of_information_statement=data['absence_of_information_statement'],
                        absence_of_information_protocol_last_updated=data['absence_of_information_protocol_last_updated'])
                    db.session.add(entry)

                entry1=Problem(
                    patient_id=data['patient_id'],
                    problem_name=data['problem_name'],
                    body_site=data['body_site'],
                    datetime_of_onset=data['datetime_of_onset'],
                    severity=data['severity'],
                    date_of_abatebent=data['date_of_abatebent'],
                    active_or_inactive=data['active_or_inactive'],
                    resolution_phase=data['resolution_phase'],
                    remission_status=data['remission_status'],
                    occurrence=data['occurrence'],
                    diagnostic_certainity=data['diagnostic_certainity'],
                    protocol_last_updated=data['protocol_last_updated'])
                db.session.add(entry1)
                db.session.commit()
                return jsonify({'success':True,'message':'Problem added successfully'}),201

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not an admin'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400


#12. Advanced Directives
# Api for get advance directives by patient 
@app.route('/api/getadvanceddirectivesbypatient',methods=['GET'])
def getAdvanceDirectivesByPatient():
    try:
        token=request.headers['token']  #Patient Token
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        if res:
            output={} 
            c = 0
            result1 = db.session.query(Advance_care_directive).filter(Advance_care_directive.patient_id==res.id).first()

            if result1:
                output['patient_id']=result1.patient_id
                output['type_of_directive']=result1.type_of_directive
                output['a_status']=result1.status
                output['description']=result1.description
                output['condition']=result1.condition
                output['directive_location']=result1.directive_location
                output['a_comment']=result1.comment
                output['valid_period_start']=result1.valid_period_start
                output['valid_period_end']=result1.valid_period_end
                output['review_due_date']=result1.review_due_date
                output['last_updated']=result1.last_updated
                output['mandate']=result1.mandate

                pat =[]  
                result2 = db.session.query(Limitation_of_treatment).filter(Limitation_of_treatment.patient_id==res.id).all()
                
                for value in result2:  
                    obj={}  
                    obj['id'] = c
                    c += 1
                    obj['patient_id']=value.patient_id
                    obj['status']=value.status
                    obj['type_of_limitation']=value.type_of_limitation
                    obj['decision']=value.decision
                    obj['qualification']=value.qualification
                    obj['rationale']=value.rationale
                    obj['patient_awareness']=value.patient_awareness
                    obj['carer_awareness']=value.carer_awareness
                    obj['comment']=value.comment
                    obj['element']=value.element
                    obj['protocol_review_date']=value.protocol_review_date
                    pat.append(obj)

                output['advance_directive']=pat     

            return jsonify({"success":True,"history":output}), 200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


# Api for get advance directives by doctor
@app.route('/api/getadvanceddirectivesbydoctor/<int:patient_id>',methods=['GET'])
def getAdvanceDirectivesByDoctor(patient_id):
    try:
        token=request.headers['token']  #Patient Token
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        if res:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()

            if patient:
                output={} 
                c = 0
                result1 = db.session.query(Advance_care_directive).filter(Advance_care_directive.patient_id==res.id).first()

                if result1:
                    output['patient_id']=result1.patient_id
                    output['type_of_directive']=result1.type_of_directive
                    output['a_status']=result1.status
                    output['description']=result1.description
                    output['condition']=result1.condition
                    output['directive_location']=result1.directive_location
                    output['a_comment']=result1.comment
                    output['valid_period_start']=result1.valid_period_start
                    output['valid_period_end']=result1.valid_period_end
                    output['review_due_date']=result1.review_due_date
                    output['last_updated']=result1.last_updated
                    output['mandate']=result1.mandate

                    pat =[]  
                    result2 = db.session.query(Limitation_of_treatment).filter(Limitation_of_treatment.patient_id==res.id).all()
                    
                    for value in result2:  
                        obj={}  
                        obj['id'] = c
                        c += 1
                        obj['patient_id']=value.patient_id
                        obj['status']=value.status
                        obj['type_of_limitation']=value.type_of_limitation
                        obj['decision']=value.decision
                        obj['qualification']=value.qualification
                        obj['rationale']=value.rationale
                        obj['patient_awareness']=value.patient_awareness
                        obj['carer_awareness']=value.carer_awareness
                        obj['comment']=value.comment
                        obj['element']=value.element
                        obj['protocol_review_date']=value.protocol_review_date
                        pat.append(obj)

                    output['advance_directive']=pat     

                return jsonify({"success":True,"history":output}), 200
            
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'not authorised, not a doctor'}), 401
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


# Api for create Advance directives history  
@app.route('/api/addadvanceddirectives',methods=['POST'])
def addadvancedDirectives():
    try:
        token = request.headers['token']   #Admin Token
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()
            if patient:
                #advance_care_directive
                advance_care_directive = Advance_care_directive.query.filter_by().first()
                if advance_care_directive:
                    advance_care_directive.type_of_directive=data['type_of_directive']
                    advance_care_directive.status=data['a_status'],description=data['description']
                    advance_care_directive.condition=data['condition']
                    advance_care_directive.directive_location=data['directive_location']
                    advance_care_directive.comment=data['a_comment']
                    advance_care_directive.valid_period_start=data['valid_period_start']
                    advance_care_directive.valid_period_end=data['valid_period_end']
                    advance_care_directive.review_due_date=data['review_due_date']
                    advance_care_directive.last_updated=data['last_updated']
                    advance_care_directive.mandate=data['mandate']
                    
                else:
                    entry = Advance_care_directive(
                            patient_id=data['patient_id'],
                            type_of_directive=data['type_of_directive'],
                            status=data['a_status'],description=data['description'],
                            condition=data['condition'],
                            directive_location=data['directive_location'],
                            comment=data['a_comment'],
                            valid_period_start=data['valid_period_start'],
                            valid_period_end=data['valid_period_end'],
                            review_due_date=data['review_due_date'],
                            last_updated=data['last_updated'],
                            mandate=data['mandate'])
                    db.session.add(entry)


                #limitation_of_treatment
                limitation_of_treatment = Limitation_of_treatment.query.filter_by().first() 
                if limitation_of_treatment:
                    limitation_of_treatment.status=data['status']
                    limitation_of_treatment.type_of_limitation=data['type_of_limitation']
                    limitation_of_treatment.decision=data['decision']
                    limitation_of_treatment.qualification=data['qualification']
                    limitation_of_treatment.rationale=data['rationale']
                    limitation_of_treatment.patient_awareness=data['patient_awareness']
                    limitation_of_treatment.carer_awareness=data['carer_awareness']
                    limitation_of_treatment.comment=data['comment']
                    limitation_of_treatment.element=data['element']
                    limitation_of_treatment.protocol_review_date=data['protocol_review_date']
                else:
                    entry1=Limitation_of_treatment(
                            patient_id=data['patient_id'],
                            status=data['status'],
                            type_of_limitation=data['type_of_limitation'],
                            decision=data['decision'],
                            qualification=data['qualification'],
                            rationale=data['rationale'],
                            patient_awareness=data['patient_awareness'],
                            carer_awareness=data['carer_awareness'],
                            comment=data['comment'],
                            element=data['element'],
                            protocol_review_date=data['protocol_review_date'])
                    db.session.add(entry1)

                db.session.commit()
                return jsonify({'success':True,'message':'history added successfully'}),201
            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, not an admin'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400
  
#13. Social History
@app.route('/api/getsocialhistoryforpatient',methods=['GET'])
def getSocialHistoryPatient():
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            pat = {}   

            result1 = db.session.query(Tobacco_smoking).filter(Tobacco_smoking.patient_uid==res.id).first()  
            if result1:
                pat['patient_id']=result1.patient_uid
                pat['status']=result1.status

            result2 = db.session.query(Alcohol_consumption).filter(Alcohol_consumption.patient_uid==res.id).first()
            if result2:    
                pat['alcohol_status']=result2.status
                pat['typical_consumption_alcohol_unit']=result2.typical_consumption_alcohol_unit
                
            return jsonify({"success":True,"history":pat}), 200

        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404       
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/getsocialhistoryfordoctor/<int:patient_id>',methods=['GET'])
def getSocialHistoryDoctor(patient_id):
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        if res:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            if patient:
                pat = {}   

                result1 = db.session.query(Tobacco_smoking).filter(Tobacco_smoking.patient_uid==res.id).first()  
                if result1:
                    pat['patient_id']=result1.patient_uid
                    pat['status']=result1.status

                result2 = db.session.query(Alcohol_consumption).filter(Alcohol_consumption.patient_uid==res.id).first()
                if result2:    
                    pat['alcohol_status']=result2.status
                    pat['typical_consumption_alcohol_unit']=result2.typical_consumption_alcohol_unit
                    
                return jsonify({"success":True,"history":pat}), 200

            else:
                return jsonify({"success":False, "message":"Not Authorised, not a patient"}), 404
        else:
            return jsonify({'success':False,'message':'not authorised, not a doctor'}), 401       
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/createsocialhistoryofpatient',methods=['POST'])
def createSocialHistoryOfPatient(): #tobacco_smoking and alcohol_consumption
    try:
        #Admin Verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query_filter_by(id = data['patient_id']).first()

            if patient:

                #tobacco_smoking
                tobacco_smoking = Tobacco_smoking.query.filter_by(patient_uid=data['patient_id']).first()
                if tobacco_smoking:
                    tobacco_smoking.status=data['smoking_status']
                else:
                    entry = Tobacco_smoking(patient_uid=data['patient_id'],status=data['smoking_status'])
                    db.session.add(entry)

                #alcohol_consumption
                alcohol_consumption = Alcohol_consumption.query.filter_by(patient_uid=data['patient_id']).first()
                if alcohol_consumption:
                    alcohol_consumption.status=data['alcohol_status']
                    alcohol_consumption.typical_consumption_alcohol_unit=data['typical_consumption_alcohol_unit']
                else:
                    entry = Alcohol_consumption(patient_uid=data['patient_id'],status=data['alcohol_status'],typical_consumption_alcohol_unit=data['typical_consumption_alcohol_unit'])
                    db.session.add(entry)

                db.session.commit()
                return jsonify({'success':True,'message':'social history added successfully'}),201

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, not an admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400

#14. Plan of Care
@app.route('/api/getplanofcareforpatient',methods=['GET'])
def getplanofcare():
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        if res:
            result1 = db.session.query(Care_plan).filter(Care_plan.patient_uid==res.id).all()
            result2 = db.session.query(Service_request).filter(Service_request.patient_uid==res.id).all()
            pat = {}   
            for value in result1:
                pat['patient_id']=value.patient_uid
                pat['care_plan_name']=value.care_plan_name
                pat['care_plan_description']=value.care_plan_description
                pat['care_plan_reason']=value.care_plan_reason
                pat['care_plan_expiry_date']=value.care_plan_expiry_date
            for value in result2:    
                pat['service_name']=value.service_name
                pat['service_type']=value.service_type
                pat['description']=value.description
                pat['reason_for_request']=value.reason_for_request
                pat['reason_description']=value.reason_description
                pat['clinical_indication']=value.clinical_indication
                pat['intent']=value.intent
                pat['urgency']=value.urgency
                pat['service_due']=value.service_due
                pat['service_period_start']=value.service_period_start
                pat['service_period_expiry']=value.service_period_expiry
                pat['indefinite']=value.indefinite
                pat['supplementary_information']=value.supplementary_information
                pat['information_description']=value.information_description
                pat['comment']=value.comment
                pat['requester_order_identifier']=value.requester_order_identifier
                pat['receiver_order_identifier']=value.receiver_order_identifier
                pat['request_status']=value.request_status
                
            return jsonify({"success":True, "planofcare":pat}), 200
             
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401     
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/getplanofcarefordoctor/<int:patient_id>',methods=['GET'])
def getplanofcarefordoctor(patient_id):
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
       
        if res:
            patient_uid = patient_id
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_uid).first()
            if patient:
                result1 = db.session.query(Care_plan).filter(Care_plan.patient_uid==patient_uid).all()
                result2 = db.session.query(Service_request).filter(Service_request.patient_uid==patient_uid).all()
                pat = {}   
                for value in result1:
                    pat['patient_id']=value.patient_uid
                    pat['care_plan_name']=value.care_plan_name
                    pat['care_plan_description']=value.care_plan_description
                    pat['care_plan_reason']=value.care_plan_reason
                    pat['care_plan_expiry_date']=value.care_plan_expiry_date
                for value in result2:    
                    pat['service_name']=value.service_name
                    pat['service_type']=value.service_type
                    pat['description']=value.description
                    pat['reason_for_request']=value.reason_for_request
                    pat['reason_description']=value.reason_description
                    pat['clinical_indication']=value.clinical_indication
                    pat['intent']=value.intent
                    pat['urgency']=value.urgency
                    pat['service_due']=value.service_due
                    pat['service_period_start']=value.service_period_start
                    pat['service_period_expiry']=value.service_period_expiry
                    pat['indefinite']=value.indefinite
                    pat['supplementary_information']=value.supplementary_information
                    pat['information_description']=value.information_description
                    pat['comment']=value.comment
                    pat['requester_order_identifier']=value.requester_order_identifier
                    pat['receiver_order_identifier']=value.receiver_order_identifier
                    pat['request_status']=value.request_status
                    
                return jsonify({'success':True,"planofcare":pat}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, Not a doctor'}), 401       
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/createplanofcareofpatient',methods=['POST'])
def createplanofcareOfPatient(): #service_request and care_plan
    try:
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:

                #care_plan
                care_plan = Care_plan.query.filter_by(patient_uid=data['patient_id']).first()
                if care_plan:
                    care_plan.patient_uid=data['patient_id']
                    care_plan.care_plan_name=data['care_plan_name']
                    care_plan.care_plan_description=data['care_plan_description']
                    care_plan.care_plan_reason=data['care_plan_reason']
                    care_plan.care_plan_expiry_date=data['care_plan_expiry_date']
                else:
                    entry = Care_plan(
                            patient_uid=data['patient_id'],
                            care_plan_name=data['care_plan_name'],
                            care_plan_description=data['care_plan_description'],
                            care_plan_reason=data['care_plan_reason'],
                            care_plan_expiry_date=data['care_plan_expiry_date'])
                    db.session.add(entry)

                #service_request
                service_request = Service_request.query.filter_by(patient_uid=data['patient_id']).first()
                if service_request:
                    service_request.service_name=data['service_name']
                    service_request.service_type=data['service_type']
                    service_request.description=data['description']
                    service_request.reason_for_request=data['reason_for_request']
                    service_request.reason_description=data['reason_description']
                    service_request.clinical_indication=data['clinical_indication']
                    service_request.intent=data['intent'],
                    service_request.urgency=data['urgency']
                    service_request.service_due=data['service_due']
                    service_request.service_period_start=data['service_period_start']
                    service_request.service_period_expiry=data['service_period_expiry']
                    service_request.indefinite=data['indefinite']
                    service_request.supplementary_information=data['supplementary_information']
                    service_request.information_description=data['information_description']
                    service_request.comment=data['comment']
                    service_request.requester_order_identifier=data['requester_order_identifier']
                    service_request.receiver_order_identifier=data['receiver_order_identifier']
                    service_request.request_status=data['request_status']
                else:
                    entry = Service_request(
                            patient_uid=data['patient_id'],
                            service_name=data['service_name'],
                            service_type=data['service_type'],
                            description=data['description'],
                            reason_for_request=data['reason_for_request'],
                            reason_description=data['reason_description'],
                            clinical_indication=data['clinical_indication'],
                            intent=data['intent'],
                            urgency=data['urgency'],
                            service_due=data['service_due'],
                            service_period_start=data['service_period_start'],
                            service_period_expiry=data['service_period_expiry'],
                            indefinite=data['indefinite'],
                            supplementary_information=data['supplementary_information'],
                            information_description=data['information_description'],
                            comment=data['comment'],
                            requester_order_identifier=data['requester_order_identifier'],
                            receiver_order_identifier=data['receiver_order_identifier'],
                            request_status=data['request_status'])
                    db.session.add(entry)
                    
                db.session.commit()
                return jsonify({'success':True,'message':'social history added successfully'}),201
                
            else:
                return jsonify({'success':False,'message':'Inavlid Patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, Not an admin'}), 401
    except Exception as e:
        print(e)
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400

#15. functional status
@app.route('/api/getfunctionalstatusforpatient',methods=['GET'])
def getfunctionalstatus():
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = Patient_details.query.filter_by(email=value['email'], password=value['password']).first()
        
        if res:
            result1 = db.session.query(Functional_status).filter(Care_plan.patient_uid==res.id).all()
            pat = {}   

            for value in result1:
                pat['patient_id']=value.patient_uid
                pat['diagnosis_name']=value.diagnosis_name
                pat['body_site']=value.body_site
                pat['date_of_onset']=value.date_of_onset
                pat['severity']=value.severity   
                pat['date_of_abatement']=value.date_of_abatement
                pat['active_inactive']=value.active_inactive
                pat['resolution_phase']=value.resolution_phase
                pat['remission_status']=value.remission_status
                pat['occurrence']=value.occurrence
                pat['diagnostic_certainty']=value.diagnostic_certainty
                pat['protocol_last_updated']=value.protocol_last_updated
                pat['clinical_impression']=value.clinical_impression
            
            return jsonify({'success':True,"functionalstatus":pat}),200
            
        else:
            return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 401     
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/getfunctionalstatusfordoctor/<int:patient_id>',methods=['GET'])
def getfunctionalstatusfordoctor(patient_id):
    try:
        token=request.headers['token']
        value = jwt.decode(token, options={"verify_signature": False})
        res = doctor_details.query.filter_by(email=value['email'], password=value['password']).first()
        if res:
            #patient verification
            patient = Patient_details.query.filter_by(id = patient_id).first()
            
            if patient:
                result1 = db.session.query(Functional_status).filter(Care_plan.patient_uid==patient_id).all()
                pat = {}   
                
                for value in result1:
                    pat['patient_id']=value.patient_uid
                    pat['diagnosis_name']=value.diagnosis_name
                    pat['body_site']=value.body_site
                    pat['date_of_onset']=value.date_of_onset
                    pat['severity']=value.severity   
                    pat['date_of_abatement']=value.date_of_abatement
                    pat['active_inactive']=value.active_inactive
                    pat['resolution_phase']=value.resolution_phase
                    pat['remission_status']=value.remission_status
                    pat['occurrence']=value.occurrence
                    pat['diagnostic_certainty']=value.diagnostic_certainty
                    pat['protocol_last_updated']=value.protocol_last_updated
                    pat['clinical_impression']=value.clinical_impression
                
                return jsonify({'success':True,"functionalstatus":pat}), 200

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not authorised, Not a doctor'}), 401       
    except:
        return jsonify({'success':False,'message':'not recieved JSON data'}),400 


@app.route('/api/createfunctionalstatus',methods=['POST'])
def createfunctionalOfPatient():
    try:
        #Admin Verification
        token = request.headers['token']
        decoded = jwt.decode(token, options={"verify_signature": False})
        admin_check= Admin_Login.query.filter_by(email=decoded["email"], password=decoded['password']).first()
        
        if admin_check:
            data=request.get_json()
            #patient verification
            patient = Patient_details.query.filter_by(id = data['patient_id']).first()

            if patient:
                
                functional_status = Functional_status.query.filter_by(patient_uid=data['patient_id']).first()
                if functional_status:
                    functional_status.diagnosis_name=data['diagnosis_name']
                    functional_status.body_site=data['body_site']
                    functional_status.date_of_onset=data['date_of_onset']
                    functional_status.severity=data['severity']
                    functional_status.date_of_abatement=data['date_of_abatement']
                    functional_status.active_inactive=data['active_inactive']
                    functional_status.resolution_phase=data['resolution_phase']
                    functional_status.remission_status=data['remission_status']
                    functional_status.occurrence=data['occurrence']
                    functional_status.diagnostic_certainty=data['diagnostic_certainty']
                    functional_status.protocol_last_updated=data['protocol_last_updated']
                    functional_status.clinical_impression=data['clinical_impression']
                else:
                    entry = Functional_status(
                            patient_uid=data['patient_id'],
                            diagnosis_name=data['diagnosis_name'],
                            body_site=data['body_site'],
                            date_of_onset=data['date_of_onset'],
                            severity=data['severity'],
                            date_of_abatement=data['date_of_abatement'],
                            active_inactive=data['active_inactive'],
                            resolution_phase=data['resolution_phase'],
                            remission_status=data['remission_status'],
                            occurrence=data['occurrence'],
                            diagnostic_certainty=data['diagnostic_certainty'],
                            protocol_last_updated=data['protocol_last_updated'],
                            clinical_impression=data['clinical_impression'])
                    db.session.add(entry)
                    
                db.session.commit()
                return jsonify({'success':True,'message':'functional status added successfully'}),201

            else:
                return jsonify({'success':False,'message':'Not Authorised, not a patient'}), 404
        else:
            return jsonify({'success':False,'message':'Not Authorised, Not Admin'}), 401
    except:
        return jsonify({'success':False,'message':'Request misses token/json data'}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0")