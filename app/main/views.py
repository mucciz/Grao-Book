from flask import render_template, request, redirect, url_for, abort, flash
from . import main
from werkzeug.urls import url_parse
from .forms import BookbookingForm, PitchavailableForm, PitchoccupationForm, CancelbookingForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import *
from app import db, create_app


@main.route('/')
@main.route('/index')
def index():

    return render_template('index.html')

@main.route('/facilities/')
def facilities():
    return render_template('facilities.html')

@main.route('/bookingbooker')
def bookingbooker():
    bookings=Booking.query.order_by(Booking.date).all()
    bookingreturns=[]
    for booking in bookings:
        bookingreturn=dict()
        bookingreturn['title']=booking.title
        # meetingreturn['team']=Team.query.filter_by(id=meeting.teamId).first().teamName
        bookingreturn['pitch']=Pitch.query.filter_by(id=booking.pitchId).first().pitchName
        bookingreturn['booker']=User.query.filter_by(id=booking.bookerId).first().fullname
        bookingreturn['date']=booking.date.date()
        bookingreturn['time']=f'{booking.startTime} to {booking.endTime}'
        bookingreturns.append(bookingreturn)
    return render_template('bookingbooker.html',bookings=bookingreturns)

@main.route('/book',methods=['GET','POST'])
@login_required
def book():
    form=BookbookingForm()
    if form.validate_on_submit():
        
        # check time collision
        bookingcollisions=Booking.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(pitchId=form.pitches.data).all()
        print(len(bookingcollisions))
        for bookingcollision in bookingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (form.startTime.data<bookingcollision.endTime and (form.startTime.data+form.duration.data)>bookingcollision.startTime):
                flash(f'The time from {bookingcollision.startTime} to {bookingcollision.endTime} is already booked by {User.query.filter_by(id=bookingcollision.bookerId).first().fullname}.')
                return redirect(url_for('main.book'))

        # make booking
        booker=current_user
    
        # team=Team.query.filter_by(id=current_user.teamId).first()
        pitch=Pitch.query.filter_by(id=form.pitches.data).first()
        cost=pitch.cost
        endTime=form.startTime.data+form.duration.data

        # participants_user=form.participants_user.data
        # participants_partner=form.participants_partner.data

        booking=Booking(title=form.title.data,pitchId=pitch.id,bookerId=booker.id,date=form.date.data,startTime=form.startTime.data,endTime=endTime,duration=form.duration.data)
        db.session.add(booking)

        # Add booking log
        # log=CostLog(title=form.title.data,teamId=team.id,teamName=team.teamName,date=form.date.data,cost=cost*form.duration.data)
        # db.session.add(log)


        db.session.commit()
        flash('Booking success!')
        return redirect(url_for('main.bookingbooker'))
    return render_template('book.html',title='Book Pitch',form=form)

@main.route('/pitchavailable',methods=['GET','POST'])
def pitchavailable():
    form=PitchavailableForm()
    if form.validate_on_submit():
        bookings=Booking.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        pitchesOccupied=set()
        for booking in bookings:
            if (form.startTime.data<booking.endTime and (form.startTime.data+form.duration.data)>booking.startTime): 
                pitchesOccupied.add(Pitch.query.filter_by(id=booking.pitchId).first())
        pitches=Pitch.query.all()
        pitchesavailable=[]
        for pitch in pitches:
            if pitch not in pitchesOccupied:
                pitchesavailable.append(pitch)
        return render_template('pitchavailablelist.html',title='Pitch available',pitches=pitchesavailable)
    return render_template('pitchavailable.html',title='Pitch availability check',form=form)




@main.route('/pitchoccupation',methods=['GET','POST'])
def pitchoccupation():
    form=PitchoccupationForm()
    if form.validate_on_submit():
        #meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
        pitchoccus=[]
        hours=range(9,23)
        pitches=Pitch.query.all()
        allpitches=[]
        for pitch in pitches:
            pitchoccu=dict()
            pitchoccu['pitchName']=pitch.pitchName
            pitchoccu['pitchhours']=[False]*14
            for hour in hours:
                bookings=Booking.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(pitchId=pitch.id).all()
                
                for booking in bookings:
                    if (hour+0.5)<booking.endTime and (hour+0.5)>booking.startTime:
                        pitchoccu['pitchhours'][hour-9]=True
                        break
            pitchoccus.append(pitchoccu)
            
            allpitches.append({'pitchName':pitch.pitchName,'cost':pitch.cost})
        return render_template('pitchoccupationlist.html',title='Pitch Occupation',pitchoccus=pitchoccus,date=form.date.data,hours=[str(hour) for hour in hours],allpitches=allpitches)
    return render_template('pitchoccupation.html',title='Pitch Occupation Status',form=form)


@main.route('/cancelbooking',methods=['GET','POST'])
@login_required
def cancelbooking():
    if not current_user.is_authenticated:
        flash('Please Log in to cancel booking')
        return redirect(url_for('auth.login')) 
    
    form=CancelbookingForm()
    if form.validate_on_submit():
        booking=Booking.query.filter_by(id=form.ids.data).first()

        if booking.date<=datetime.now():
            flash(f'Past booking cannot be canceled')
            return redirect(url_for('main.cancelbooking'))
        
        db.session.delete(booking)
        db.session.commit()
        flash('Booking successfully deleted!')
        return redirect(url_for('main.index'))
    return render_template('cancelbooking.html',title='Cancel Booking',form=form)









































































































































































































# @main.route('/')
# @main.route('/index')
# def index():
#     return render_template('index.html')

# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('main.login'))
#         login_user(user, remember=form.remember_me.data)
#         next_page=request.args.get('next')
#         if not next_page or url_parse(next_page).netloc!='':
#             next_page=url_for('main.index')
#         return redirect(next_page)
#     return render_template('login.html', title='Sign In', form=form)

# @main.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('main.index'))

# @main.route('/register', methods=['GET','POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#     form =RegistrationForm()
#     if form.validate_on_submit():
#         user=User(username=form.username.data,\
#                   fullname=form.fullname.data,\
#                   position=form.position.data,\
#                   password = form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         return redirect(url_for('main.login'))
#     return render_template('register.html',title='Register',form=form)

# @main.route('/adduser', methods=['GET','POST'])
# @login_required
# def adduser():
#     if not current_user.is_authenticated:
#         flash('Please Log in as admin to add user')
#         return redirect(url_for('main.login'))
#     if current_user.username!='admin':
#         flash('Please Log in as admin to add user')
#         return redirect(url_for('main.index'))
#     form =AdduserForm()
#     if form.validate_on_submit():
#         user=User(username=form.username.data,\
#                   fullname=form.fullname.data,\
#                   position=form.position.data,\
#                   teamId=form.teamId.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         team=Team.query.filter_by(id=user.teamId).first()
#         if team is None:
#             newTeam=Team(id=user.teamId,\
#                          teamName=form.teamName.data)
#             db.session.add(newTeam)
#             db.session.commit()
#             flash(f'Added user {form.username.data} with a new team created')
#             return redirect(url_for('main.adduser'))
#         else:
#             db.session.commit()
#             flash(f'Added user {form.username.data} to an existing team')
#             return redirect(url_for('main.adduser'))
#     return render_template('adduser.html',title='Add User',form=form)

# @main.route('/addteam',methods=['GET','POST'])
# @login_required
# def addteam():
#     if not current_user.is_authenticated:
#         flash('Please Log in as admin to add team')
#         return redirect(url_for('main.login'))
#     if current_user.username!='admin':
#         flash('Please Log in as admin to add team')
#         return redirect(url_for('main.index'))
#     form=AddteamForm()
#     if form.validate_on_submit():
#         team=Team(id=form.id.data,\
#                   teamName=form.teamName.data)
#         db.session.add(team)
#         db.session.commit()
#         flash(f'Team {form.teamName.data} successfully added!')
#         return redirect(url_for('main.addteam'))
#     return render_template('addteam.html',title='Add Team',form=form)

# @main.route('/deleteteam',methods=['GET','POST'])
# @login_required
# def deleteteam():
#     if not current_user.is_authenticated:
#         flash('Please Log in as admin to delete team')
#         return redirect(url_for('main.login'))
#     if current_user.username!='admin':
#         flash('Please Log in as admin to delete team')
#         return redirect(url_for('main.index'))
#     form=DeleteteamForm()

#     if form.validate_on_submit():
#         team=Team.query.filter_by(id=form.ids.data).first()

#         meetings=Meeting.query.filter_by(teamId=team.id).all()
#         hasFutureBooking=False
#         for meeting in meetings:
#             if meeting.date>datetime.now():
#                 hasFutureBooking=True
#                 break
#         if hasFutureBooking:
#             flash('You cannot delete a team that holds future bookings!')
#             return redirect(url_for('main.deleteteam'))

#         # delete all users in a deleted team
#         userInTeam=User.query.filter_by(teamId=form.ids.data).all()
#         for user in userInTeam:
#             db.session.delete(user)
#         db.session.delete(team)
#         db.session.commit()
#         flash(f'Team {team.teamName} and team members successfully deleted! Please register member again to other team')
#         return redirect(url_for('main.index'))
#     form=DeleteteamForm()
#     return render_template('deleteteam.html',title='Delete Team',form=form)

# @main.route('/deleteuser',methods=['GET','POST'])
# @login_required
# def deleteuser():
#     if not current_user.is_authenticated:
#         flash('Please Log in as admin to delete user')
#         return redirect(url_for('main.login'))
#     if current_user.username!='admin':
#         flash('Please Log in as admin to delete user')
#         return redirect(url_for('main.index'))

#     form=DeleteuserForm()
#     if form.validate_on_submit():
#         user=User.query.filter_by(id=form.ids.data).first()

#         meetings=Meeting.query.filter_by(bookerId=user.id).all()
#         hasFutureBooking=False
#         for meeting in meetings:
#             if meeting.date>datetime.now():
#                 hasFutureBooking=True
#                 break
#         if hasFutureBooking:
#             flash('You cannot delete a user that holds future bookings!')
#             return redirect(url_for('main.deleteuser'))

#         db.session.delete(user)
#         db.session.commit()
#         flash(f'User {user.username} successfully deleted! ')
#         return redirect(url_for('main.index'))
#     return render_template('deleteuser.html',title='Delete User',form=form)

# @main.route('/book',methods=['GET','POST'])
# @login_required
# def book():
#     form=BookmeetingForm()
#     if form.validate_on_submit():

#         # check time collision
#         meetingcollisions=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=form.rooms.data).all()
#         print(len(meetingcollisions))
#         for meetingcollision in meetingcollisions:
#             # [a, b] overlaps with [x, y] iff b > x and a < y
#             if (form.startTime.data<meetingcollision.endTime and (form.startTime.data+form.duration.data)>meetingcollision.startTime):
#                 flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().fullname}.')
#                 return redirect(url_for('main.book'))

#         # make booking
#         booker=current_user

#         team=Team.query.filter_by(id=current_user.teamId).first()
#         room=Room.query.filter_by(id=form.rooms.data).first()
#         cost=room.cost
#         endTime=form.startTime.data+form.duration.data

#         participants_user=form.participants_user.data
#         participants_partner=form.participants_partner.data

#         meeting=Meeting(title=form.title.data,teamId=team.id,roomId=room.id,bookerId=booker.id,date=form.date.data,startTime=form.startTime.data,endTime=endTime,duration=form.duration.data)
#         db.session.add(meeting)

#         # Add booking log
#         log=CostLog(title=form.title.data,teamId=team.id,teamName=team.teamName,date=form.date.data,cost=cost*form.duration.data)
#         db.session.add(log)

#         # Add participants records
#         for participant in participants_user:
#             participating=Participants_user(meeting=form.title.data,userId=participant)
#             db.session.add(participating)
#         for participant in participants_partner:
#             participating=Participants_partner(meeting=form.title.data,partnerId=participant)
#             db.session.add(participating)

#         db.session.commit()
#         flash('Booking success!')
#         return redirect(url_for('main.index'))
#     return render_template('book.html',title='Book Meeting',form=form)

# @main.route('/cancelbooking',methods=['GET','POST'])
# @login_required
# def cancelbooking():
#     if not current_user.is_authenticated:
#         flash('Please Log in to cancel booking')
#         return redirect(url_for('main.login'))

#     form=CancelbookingForm()
#     if form.validate_on_submit():
#         meeting=Meeting.query.filter_by(id=form.ids.data).first()

#         if meeting.date<=datetime.now():
#             flash(f'Past booking cannot be canceled')
#             return redirect(url_for('main.cancelbooking'))

#         participants_user=Participants_user.query.filter_by(meeting=meeting.title).all()
#         for part in participants_user:
#             db.session.delete(part)
#         participants_partner=Participants_partner.query.filter_by(meeting=meeting.title).all()
#         for part in participants_partner:
#             db.session.delete(part)

#         costlog=CostLog.query.filter_by(title=meeting.title).first()
#         db.session.delete(costlog)

#         db.session.delete(meeting)
#         db.session.commit()
#         flash(f'Meeting {meeting.title} successfully deleted! ')
#         return redirect(url_for('main.index'))
#     return render_template('cancelbooking.html',title='Cancel Meeting',form=form)

# @main.route('/roomavailable',methods=['GET','POST'])
# def roomavailable():
#     form=RoomavailableForm()
#     if form.validate_on_submit():
#         meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
#         roomsOccupied=set()
#         for meeting in meetings:
#             if (form.startTime.data<meeting.endTime and (form.startTime.data+form.duration.data)>meeting.startTime):
#                 roomsOccupied.add(Room.query.filter_by(id=meeting.roomId).first())
#         rooms=Room.query.all()
#         roomsavailable=[]
#         for room in rooms:
#             if room not in roomsOccupied:
#                 roomsavailable.append(room)
#         return render_template('roomavailablelist.html',title='Room available',rooms=roomsavailable)
#     return render_template('roomavailable.html',title='Room availability check',form=form)

# @main.route('/roomoccupation',methods=['GET','POST'])
# def roomoccupation():
#     form=RoomoccupationForm()
#     if form.validate_on_submit():
#         #meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).all()
#         roomoccus=[]
#         hours=range(9,23)
#         rooms=Room.query.all()
#         allrooms=[]
#         for room in rooms:
#             roomoccu=dict()
#             roomoccu['roomName']=room.roomName
#             roomoccu['roomhours']=[False]*14
#             for hour in hours:
#                 meetings=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=room.id).all()

#                 for meeting in meetings:
#                     if (hour+0.5)<meeting.endTime and (hour+0.5)>meeting.startTime:
#                         roomoccu['roomhours'][hour-9]=True
#                         break
#             roomoccus.append(roomoccu)

#             allrooms.append({'roomName':room.roomName,'tel':'Yes' if room.telephone else 'No','pro':'Yes' if room.projector else 'No',\
#                              'wb':'Yes' if room.whiteboard else 'No','cost':room.cost})
#         return render_template('roomoccupationlist.html',title='Room Occupation',roomoccus=roomoccus,date=form.date.data,hours=[str(hour) for hour in hours],allrooms=allrooms)
#     return render_template('roomoccupation.html',title='Room Occupation Status',form=form)

# @main.route('/meetingbooker')
# def meetingbooker():
#     meetings=Meeting.query.order_by(Meeting.date).all()
#     meetingreturns=[]
#     for meeting in meetings:
#         meetingreturn=dict()
#         meetingreturn['title']=meeting.title
#         meetingreturn['team']=Team.query.filter_by(id=meeting.teamId).first().teamName
#         meetingreturn['room']=Room.query.filter_by(id=meeting.roomId).first().roomName
#         meetingreturn['booker']=User.query.filter_by(id=meeting.bookerId).first().fullname
#         meetingreturn['date']=meeting.date.date()
#         meetingreturn['time']=f'{meeting.startTime} to {meeting.endTime}'
#         meetingreturns.append(meetingreturn)
#     return render_template('meetingbooker.html',meetings=meetingreturns)

# @main.route('/meetingparticipants',methods=['GET','POST'])
# def meetingparticipants():
#     form=MeetingparticipantsForm()
#     if form.validate_on_submit():
#         meeting=Meeting.query.filter_by(id=form.ids.data).first()
#         participants=[]
#         participants_user=Participants_user.query.filter_by(meeting=meeting.title).all()
#         participants_partner=Participants_partner.query.filter_by(meeting=meeting.title).all()
#         for part in participants_user:
#             participants.append(f'{User.query.filter_by(id=part.userId).first().fullname} from {Team.query.filter_by(id=User.query.filter_by(id=part.userId).first().teamId).first().teamName}')
#         for part in participants_partner:
#             participants.append(f'partner {Businesspartner.query.filter_by(id=part.partnerId).first().name} from {Businesspartner.query.filter_by(id=part.partnerId).first().representing}')
#         return render_template('meetingparticipants.html',title='Meeting Participants',meetingtitle=meeting.title,participants=participants)
#     return render_template('meetingparticipantscheck.html',title='Meeting Participants',form=form)

# @main.route('/costs',methods=['GET','POST'])
# def costs():
#     form=CostaccruedForm()
#     if form.validate_on_submit():
#         costlogs=CostLog.query.filter(CostLog.date>=datetime.combine(form.startdate.data,datetime.min.time())).filter(CostLog.date<=datetime.combine(form.enddate.data,datetime.min.time())).all()
#         teams=list(set([costlog.teamName for costlog in costlogs]))
#         teamcosts=[]
#         # slow implementation, can be optimized
#         for team in teams:
#             teamcost=dict()
#             teamcost['teamName']=team
#             teamcost['total']=0
#             for costlog in costlogs:
#                 if costlog.teamName==team:
#                     teamcost['total']+=costlog.cost
#             teamcosts.append(teamcost)
#         return render_template('costs.html',title='Cost Accrued',startdate=form.startdate.data,enddate=form.enddate.data,teamcosts=teamcosts)
#     return render_template('costcheck.html',title='Cost Accrued check',form=form)
