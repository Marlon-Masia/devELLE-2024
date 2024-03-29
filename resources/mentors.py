from flask_jwt_extended import jwt_required
from flask_restful import Resource
from utils import *
from exceptions_util import *

MENTOR_QUESTION_TYPE_1 = "MENTOR_FR"
MENTOR_QUESTION_TYPE_2 = "MENTOR_MC"

#saves the user's preferred mentor
class MentorPreference(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['mentor_name'] = getParameter("mentor_name", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            updated = store_mentor_preference(user_id, data['mentor_name'], conn, cursor)

            if updated:
                raise ReturnSuccess('Mentor preference updated.', 200)
            else:
                raise ReturnSuccess('Mentor preference created.', 201)
        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()

    @jwt_required
    def get(self):
        # data = {}
        # data['user_id'] = getParameter("user_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            mentorPreference = get_mentor_preference(user_id, conn, cursor)

            raise ReturnSuccess(mentorPreference[0][0], 200)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()

#store Create, Read, Update student answers to Mentor Questions
class StudentResponses(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['response'] = getParameter("response", str, True, "")
        data['question_id'] = getParameter("question_id", str, True, "")
        data['session_id'] = getParameter("session_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            store_student_response(data['question_id'], data['response'], data['session_id'], conn, cursor)

            raise ReturnSuccess('Student response created for question %s.' % data['question_id'], 201)
        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()

    @jwt_required
    def get(self):
        data = {}
        data['session_id'] = getParameter("session_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            db_result = get_student_response(data['session_id'], conn, cursor)
            studentResponses = [];
            for result in db_result:
                sr_record = {
                    'mentorResponseID' : result[0],
                    'questionID' : result[1],
                    'sessionID' : result[2],
                    'response' : result[3],
                }
                studentResponses.append(sr_record)

            if studentResponses:
                raise ReturnSuccess(studentResponses, 200)
            else:
                raise ReturnSuccess("No associated logged mentor responses found for that module and/or user", 200)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()

#Create mentor questions
class CreateMentorQuestions(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['type'] = getParameter("type", str, True, "")
        data['question_text'] = getParameter("question_text", str, True, "")
        data['moduleID'] = getParameter("moduleID", str, True, "")
        data['mc_options'] = getParameter("mc_options", list, False, "")
        # A tuple example: (1, "value", 3.2, 5)
        # A list of values in parentheses separated by commas
        # Send values as [["option1", "option2"]]

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            frQuestionCreated = store_mentor_question(data['type'], data['question_text'], conn, cursor, data['mc_options'])

            query = "SELECT MAX(`questionID`) FROM `question`"
            result = getFromDB(query, None, conn, cursor)
            question_id = check_max_id(result) - 1

            if data['moduleID']:
                query = "INSERT INTO `module_question` (`moduleID`, `questionID`) VALUES (%s, %s)"
                postToDB(query, (data['moduleID'], question_id), conn, cursor)

            if frQuestionCreated:
                raise ReturnSuccess('Mentor Free Response Question Stored.', 201)
            else:
                raise ReturnSuccess('Mentor Multiple Choice Question Stored.', 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()

class GetMentorQuestions(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['moduleID'] = getParameter("moduleID", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:

            conn = mysql.connect()
            cursor = conn.cursor()

            result = get_mentor_questions(data['moduleID'], conn, cursor)

            mentorQuestions = []
            for row in result:
                question = {}
                question['questionID'] = row[0]
                question['type'] = row[1]
                question['questionText'] = row[2]
                mentorQuestions.append(question)

            raise ReturnSuccess(mentorQuestions, 200)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()

#Modify mentor questions
class ModifyMentorQuestions(Resource):
    @jwt_required
    def post(self):
        data = {}

        data['question_text'] = getParameter("question_text", str, True, "")
        data['question_id'] = getParameter("question_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            questionModified = modify_mentor_question(data['question_id'], data['question_text'], conn, cursor)

            if questionModified:
                raise ReturnSuccess('Question Updated.', 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()

class DeleteMentorQuestion(Resource):
    @jwt_required
    def delete(self):
        data = {}
        data['questionID'] = getParameter("question_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        if permission == 'st' and not is_ta(user_id, data['groupID']):
            return errorMessage("User not authorized to delete questions."), 400

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            question_query = "SELECT * FROM `question` WHERE `questionID` = %s"
            question_data = getFromDB(question_query, data['questionID'], conn, cursor)

            if question_data:

                delete_query = "INSERT INTO `deleted_question` (`questionID`, `audioID`, `imageID`, `type`, `questionText`) VALUES (%s, %s, %s, %s, %s)"
                postToDB(delete_query, (question_data[0][0], question_data[0][1], question_data[0][2], question_data[0][3], question_data[0][4]), conn, cursor)

                response_query = "SELECT `mentorResponseID` FROM `mentor_responses` WHERE `questionID` = %s"
                response_results = getFromDB(response_query, (question_data[0][0]), conn, cursor)

                for response in response_results:
                    response_query = "UPDATE `mentor_responses` SET `questionID` = %s, `deleted_questionID` = %s WHERE `mentorResponseID` = %s"
                    postToDB(response_query, (None, question_data[0][0], response[0]), conn, cursor)

                mc_choice_query = "DELETE FROM `multiple_choice_answers` WHERE `questionID` = %s"
                deleteFromDB(mc_choice_query, data['questionID'], conn, cursor)

                query = "DELETE FROM `question` WHERE `questionID` = %s"
                deleteFromDB(query, data['questionID'], conn, cursor)

                raise ReturnSuccess("Successfully deleted question and answer set!", 201)
            else:
                raise CustomException("No question with that ID exist!", 201)
        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()



class GetMultipleChoiceOptions(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['question_id'] = getParameter("question_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            result = get_mc_options(data['question_id'], conn, cursor)
            mc_options = []
            for row in result:
                mc_option = {}
                mc_option['multipleChoiceID'] = row[0]
                mc_option['questionID'] = row[1]
                mc_option['answerChoice'] = row[2]
                mc_options.append(mc_option)

            raise ReturnSuccess(mc_options, 200)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()



class ModifyMultipleChoiceOption(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['updated_option'] = getParameter("updated_option", str, True, "")
        data['mc_id'] = getParameter("mc_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            modify_mc_options(data['updated_option'], data['mc_id'], conn, cursor)
            raise ReturnSuccess("Successfully updated multiple choice option", 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()

class CreateMultipleChoiceOption(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['option'] = getParameter("option", str, True, "")
        data['question_id'] = getParameter("question_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            create_mc_option(data['option'], data['question_id'], conn, cursor)
            raise ReturnSuccess("Successfully created multiple choice option", 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if(conn.open):
                cursor.close()
                conn.close()


class DeleteMultipleChoiceOption(Resource):
    @jwt_required
    def delete(self):
        data = {}
        data['multipleChoiceID'] = getParameter("mc_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            delete_mc_option(data['multipleChoiceID'], conn, cursor)
            raise ReturnSuccess("Successfully deleted multiple choice option", 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()

class CreateMentorQuestionFrequency(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['numIncorrectCards'] = getParameter("numIncorrectCards", str, False, "")
        data['numCorrectCards'] = getParameter("numCorrectCards", str, False, "")
        data['time'] = getParameter("time", str, False, "")
        data['moduleID'] = getParameter("module_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            if(set_mentor_question_frequency(data['moduleID'], data['numIncorrectCards'], data['numCorrectCards'], data['time'], conn, cursor)):
                raise ReturnSuccess("Successfully created mentor question frequency", 201)
            else:
                raise ReturnSuccess("Frequency updated for the module", 201)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()


class GetMentorQuestionFrequency(Resource):
    @jwt_required
    def post(self):
        data = {}
        data['moduleID'] = getParameter("module_id", str, True, "")

        permission, user_id = validate_permissions()
        if not permission or not user_id:
            return errorMessage("Invalid user"), 401

        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            db_result = get_mentor_question_frequency(data['moduleID'], conn, cursor)
            questionFrequencies = []
            for result in db_result:
                sr_record = {
                    'incorrectCardsFreq': result[1],
                    'correctCardsFreq': result[2],
                    'time': result[3],
                    'moduleID': result[4],
                }
                questionFrequencies.append(sr_record)

            raise ReturnSuccess(questionFrequencies, 200)

        except CustomException as error:
            conn.rollback()
            return error.msg, error.returnCode
        except ReturnSuccess as success:
            conn.commit()
            return success.msg, success.returnCode
        except Exception as error:
            conn.rollback()
            return errorMessage(str(error)), 500
        finally:
            if (conn.open):
                cursor.close()
                conn.close()

