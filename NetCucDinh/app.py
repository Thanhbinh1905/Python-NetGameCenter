from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from connectDb import connect_sql_server, execute_query, close_resources
import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đặt secret key của bạn ở đây

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "SELECT UserID, Permission FROM Users WHERE Username = ? AND Password = ?"
        
        cursor.execute(query, (username,password))
        user = cursor.fetchone()
        if user:    
            session['user_id'] = user[0]  # Lưu UserID vào session
            permission = user[1]  # Lấy giá trị Permission
            session['permission'] = user[1]
            flash('Login successful!', 'success')
            # Kiểm tra giá trị của Permission để điều hướng người dùng đến trang tương ứng
            if permission == 0:
                return redirect(url_for('main_menu'))
            elif permission == 1:
                return redirect(url_for('admin_manage'))
            else:
                flash('Invalid permission level', 'danger')
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('home'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('home'))
    finally:
        close_resources(cursor, conn)

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Xóa session user_id khi logout
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/admin_manage')
def admin_manage():
    if 'user_id' in session and session['permission'] == 1:
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            
            top5usage_query = """
            SELECT TOP 5
                s.SeatID,
                COUNT(u.UsageID) AS UsageCount
            FROM 
                Seats s
            LEFT JOIN 
                Usage u ON s.SeatID = u.SeatID
            GROUP BY 
                s.SeatID
            ORDER BY 
                UsageCount DESC;
            """
            cursor.execute(top5usage_query)
            datatop5 = cursor.fetchall()

            # Query hien thi doanh thu
            revenue_query = """
            SELECT Date, TotalAmount FROM Revenue
            """
            cursor.execute(revenue_query)
            revenue_data = cursor.fetchall()

            # Query hien thi computer config
            computers_query = """
            SELECT * FROM Computers
            """
            cursor.execute(computers_query)
            computers_data = cursor.fetchall()

            # Query to get today's revenue
            revenue_today_query = """
            SELECT 
                SUM(Amount) AS TotalAmount
            FROM 
                Payments
            WHERE 
                CAST(PaymentTime AS DATE) = CAST(GETDATE() AS DATE);
            """
            cursor.execute(revenue_today_query)
            revenue_today = cursor.fetchone()

            # Fetch total amount from the query result
            total_amount_today = revenue_today[0] if revenue_today[0] is not None else 0

            # Query to get seat activated counter
            Usage_activated_query = """
            SELECT COUNT(*) AS ActiveUsageCount
            FROM Usage
            WHERE IsActive = 1;
            """
            cursor.execute(Usage_activated_query)
            usage_activated = cursor.fetchone()

            # Query to get seat
            seat_query = """
            SELECT s.SeatID, c.Configurations 
            FROM Seats s
            INNER JOIN Computers c ON s.ComputerID = c.ComputerID
            """
            cursor.execute(seat_query)
            seats_computers_data = cursor.fetchall()

            # Fetch total amount from the query result
            total_activated = usage_activated[0] if usage_activated[0] is not None else 0

            return render_template('admin_manage.html', datatop5=datatop5, revenue_data=revenue_data, total_amount_today = total_amount_today, total_activated = total_activated, computers_data = computers_data, seats_computers_data = seats_computers_data)
        except Exception as e:
            print(f"Error: {e}")
            flash('Error fetching data from database', 'danger')
            return redirect(url_for('home'))
        finally:
            close_resources(cursor, conn)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('home'))

@app.route('/user_mng')
def user_mng():
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        user_query = """
            SELECT UserID, Username, Fullname, Phone, Permission FROM Users
            """
        cursor.execute(user_query)
        user_data = cursor.fetchall()
        
        flash('User data fetched successfully!', 'success')
        return render_template('user_mng.html', user_data=user_data)
    
    except Exception as e:
        print(f"Error: {e}")
        flash('Error fetching data from database', 'danger')
        return redirect(url_for('home'))
    finally:
        close_resources(cursor, conn)

    

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    fullname = request.form['fullname']
    phone = request.form['phone']
    permission = request.form['permission']

    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "INSERT INTO Users (Username, Password, Fullname, Phone, Permission) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(query, (username, password, fullname, phone, permission))
        conn.commit()
        flash('User added successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        close_resources(cursor, conn)
    return redirect(url_for('user_mng'))


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        phone = request.form['phone']
        permission = request.form['permission']
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "UPDATE Users SET Username = ?, Password = ?, Fullname = ?, Phone = ?, Permission = ? WHERE UserID = ?"
            cursor.execute(query, (username, password, fullname, phone, permission, user_id,))
            conn.commit()
            flash('User updated successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            close_resources(cursor, conn)
        return redirect(url_for('user_mng'))
    else:
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "SELECT * FROM Users WHERE UserID = ?"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            return render_template('edit_user.html', user=user)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('user_mng'))
        finally:
            close_resources(cursor, conn)



@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "DELETE FROM Users WHERE UserID=?"
        cursor.execute(query, (user_id,))
        conn.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        close_resources(cursor, conn)
    return redirect(url_for('user_mng'))

@app.route('/add_seat', methods=['POST'])
def add_seat():
    seat_id = request.form['seat_id']
    computer_id = request.form['computer_id']
    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "INSERT INTO Seats (SeatID, ComputerID) VALUES (?, ?)"
        cursor.execute(query, (seat_id, computer_id))
        conn.commit()
        flash('Seat added successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        close_resources(cursor, conn)
    return redirect(url_for('admin_manage'))


@app.route('/edit_seat/<int:seat_id>', methods=['GET', 'POST'])
def edit_seat(seat_id):
    if request.method == 'POST':
        computer_id = request.form['computer_id']
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "UPDATE Seats SET ComputerID = ? WHERE SeatID = ?"
            cursor.execute(query, (computer_id, seat_id))
            conn.commit()
            flash('Seat updated successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            close_resources(cursor, conn)
        return redirect(url_for('admin_manage'))
    else:
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "SELECT * FROM Seats WHERE SeatID = ?"
            cursor.execute(query, (seat_id,))
            seat = cursor.fetchone()
            return render_template('edit_seat.html', seat=seat)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin_manage'))
        finally:
            close_resources(cursor, conn)


@app.route('/delete_seat/<int:seat_id>', methods=['POST'])
def delete_seat(seat_id):
    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "DELETE FROM Seats WHERE SeatID = ?"
        cursor.execute(query, (seat_id,))
        conn.commit()
        flash('Seat deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        close_resources(cursor, conn)
    return redirect(url_for('admin_manage'))


@app.route('/delete_computer/<int:computer_id>', methods=['POST'])
def delete_computer(computer_id):
    conn = None
    cursor = None
    try:
        conn = connect_sql_server()
        cursor = conn.cursor()
        query = "DELETE FROM Computers WHERE ComputerID = ?"
        cursor.execute(query, (computer_id,))
        conn.commit()
        flash('Computer configuration deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        close_resources(cursor, conn)
    return redirect(url_for('admin_manage'))

@app.route('/edit_computer/<int:computer_id>', methods=['GET', 'POST'])
def edit_computer(computer_id):
    if request.method == 'POST':
        # Xử lý việc cập nhật thông tin computer
        new_details = request.form['details']
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "UPDATE Computers SET Configurations = ? WHERE ComputerID = ?"
            cursor.execute(query, (new_details, computer_id))
            conn.commit()
            flash('Computer updated successfully!', 'success')
            return redirect(url_for('admin_manage'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin_manage'))
        finally:
            close_resources(cursor, conn)
    else:
        # Lấy thông tin hiện tại của computer
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "SELECT * FROM Computers WHERE ComputerID = ?"
            cursor.execute(query, (computer_id,))
            computer_data = cursor.fetchone()
            return render_template('edit_computer.html', computer_data=computer_data)
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin_manage'))
        finally:
            close_resources(cursor, conn)

@app.route('/add_computer', methods=['GET', 'POST'])
def add_computer():
    if request.method == 'POST':
        config = request.form['config']
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            query = "INSERT INTO Computers (Configurations) VALUES (?)"
            cursor.execute(query, (config,))
            conn.commit()
            flash('Computer configuration added successfully!', 'success')
            return redirect(url_for('admin_manage'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin_manage'))
        finally:
            close_resources(cursor, conn)
    else:
        return render_template('add_computer.html')

@app.route('/main_menu')
def main_menu():
    if 'user_id' in session and session['permission'] == 0:
        try:
            conn = connect_sql_server()
            
            query = """
            SELECT s.SeatID, 
                c.Configurations, 
                CASE
                    WHEN u.IsActive = 1 THEN 'Active'
                    ELSE 'Inactive'
                END AS Status,
                u.StartTime
            FROM Seats s
            INNER JOIN Computers c ON s.ComputerID = c.ComputerID
            LEFT JOIN Usage u ON s.SeatID = u.SeatID AND u.IsActive = 1;
            """
            
            cursor = execute_query(conn, query)
            data = cursor.fetchall()

            close_resources(cursor, conn)

            return render_template('main_menu.html', data=data)
        except Exception as e:
            print(f"Error: {e}")
            flash('Error fetching data from database', 'danger')
            return redirect(url_for('home'))
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('home'))
    
@app.route('/report')
def report():
    if 'user_id' in session:
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()
            
            top5usage_query = """
            SELECT TOP 5
                s.SeatID,
                COUNT(u.UsageID) AS UsageCount
            FROM 
                Seats s
            LEFT JOIN 
                Usage u ON s.SeatID = u.SeatID
            GROUP BY 
                s.SeatID
            ORDER BY 
                UsageCount DESC;
            """
            cursor.execute(top5usage_query)
            datatop5 = cursor.fetchall()

            revenue_query = """
            SELECT Date, TotalAmount FROM Revenue
            """
            cursor.execute(revenue_query)
            revenue_data = cursor.fetchall()

            # Query to get today's revenue
            revenue_today_query = """
            SELECT 
                SUM(Amount) AS TotalAmount
            FROM 
                Payments
            WHERE 
                CAST(PaymentTime AS DATE) = CAST(GETDATE() AS DATE);
            """
            cursor.execute(revenue_today_query)
            revenue_today = cursor.fetchone()

            # Fetch total amount from the query result
            total_amount_today = revenue_today[0] if revenue_today[0] is not None else 0

            # Query to get seat activated counter
            Usage_activated_query = """
            SELECT COUNT(*) AS ActiveUsageCount
            FROM Usage
            WHERE IsActive = 1;
            """
            cursor.execute(Usage_activated_query)
            usage_activated = cursor.fetchone()

            # Fetch total amount from the query result
            total_activated = usage_activated[0] if usage_activated[0] is not None else 0

            return render_template('reportday.html', datatop5=datatop5, revenue_data=revenue_data, total_amount_today = total_amount_today, total_activated = total_activated)
        except Exception as e:
            print(f"Error: {e}")
            flash('Error fetching data from database', 'danger')
            return redirect(url_for('home'))
        finally:
            close_resources(cursor, conn)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('home'))



@app.route('/filter_table', methods=['POST'])
def filter_table():
    seat_id = request.form.get('seat_id')
    try:
        conn = connect_sql_server()

        query = """
        SELECT Seats.SeatID, Computers.ComputerID, Computers.Configurations, Usage.StartTime,
               CASE 
                   WHEN Usage.EndTime IS NULL AND Usage.IsActive = 1 THEN 'Active' 
                   ELSE 'Inactive' 
               END AS Status
        FROM Seats
        LEFT JOIN Computers ON Seats.ComputerID = Computers.ComputerID
        LEFT JOIN Usage ON Seats.SeatID = Usage.SeatID
        WHERE Seats.SeatID = ?
        """
        
        cursor = execute_query(conn, query, (seat_id,))
        data = cursor.fetchall()

        close_resources(cursor, conn)

        return render_template('main_menu.html', data=data)
    except Exception as e:
        print(f"Error: {e}")
        flash('Error filtering data from database', 'danger')
        return redirect(url_for('main_menu'))

@app.route('/start_seat', methods=['POST'])
def start_seat():
    data = request.get_json()
    seat_id = data.get('seat_id')

    if seat_id:
        try:
            conn = connect_sql_server()
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO Usage (SeatID, StartTime, IsActive) VALUES (?, ?, ?)"
            cursor = execute_query(conn, query, (seat_id, current_time, 1))
            conn.commit()

            # Return success message (optional)
            return jsonify({'status': 'success', 'message': 'Seat started successfully.'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

        finally:
            close_resources(cursor, conn)

    return jsonify({'status': 'error', 'message': 'Invalid seat ID provided.'})

# Route to handle stopping a seat
@app.route('/stop_seat/<int:seat_id>', methods=['GET'])
def stop_seat(seat_id):
    user_id = session.get('user_id')  # Retrieve UserID from session if needed

    try:
        conn = connect_sql_server()
        
        # Retrieve start_time and end_time from the database
        query = "SELECT StartTime FROM Usage WHERE SeatID = ? AND IsActive = 1"
        cursor = execute_query(conn, query, (seat_id,))
        usage_record = cursor.fetchone()

        if not usage_record:
            flash('Usage record not found or seat is not active.', 'danger')
            return redirect(url_for('main_menu'))

        start_time = usage_record[0]
        end_time = datetime.datetime.now()
        end_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not start_time or not end_time:
            flash('Invalid start or end time for the seat.', 'danger')
            return redirect(url_for('main_menu'))

        # Calculate the duration in hours
        duration_seconds = (end_time - start_time).total_seconds()
        duration_hours = duration_seconds / 3600
        
        if duration_hours < 0:
            flash('Invalid duration calculation, please check.', 'danger')
            return redirect(url_for('main_menu'))

        amount = round(duration_hours * 20000, 2)  # Calculate amount based on hours

        # Render the payment page with necessary details
        return render_template('payment.html', seat_id=seat_id, start_time=start_time, end_time=end_time_str, amount=amount)

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('main_menu'))

    finally:
        close_resources(cursor, conn)



@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    data = request.get_json()

    seat_id = data.get('seat_id')
    amount = float(data.get('amount'))  # Ensure amount is converted to float
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    user_id = session.get('user_id')  # Ensure UserID is retrieved from session

    if seat_id and amount and user_id:
        conn = None
        cursor = None
        try:
            conn = connect_sql_server()
            cursor = conn.cursor()

            # Retrieve UsageID based on start_time and end_time
            query_get_usage_id = """
            SELECT TOP 1 UsageID
            FROM Usage
            WHERE SeatID = ? AND IsActive=1
            ORDER BY ABS(DATEDIFF(second, StartTime, GETDATE()))
            """
            cursor.execute(query_get_usage_id, (seat_id,))
            usage_record = cursor.fetchone()

            if not usage_record:
                return jsonify({'status': 'error', 'message': 'Usage record not found for the given parameters.'})

            usage_id = usage_record[0]

            # Insert a new payment record
            payment_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query_insert_payment = """
            INSERT INTO Payments (UserID, UsageID, Amount, PaymentTime)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(query_insert_payment, (user_id, usage_id, amount, payment_time))
            conn.commit()

            # Update Usage table to mark seat as inactive
            current_time = end_time
            query_update_usage = "UPDATE Usage SET EndTime=?, IsActive=? WHERE SeatID=? AND IsActive=1"
            cursor.execute(query_update_usage, (current_time, 0, seat_id))
            conn.commit()

            # Update revenue by date
            cursor.execute("EXEC UpdateRevenueByDate")
            conn.commit()

            # Return success response
            return jsonify({'status': 'success', 'message': 'Payment successful.'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

        finally:
            close_resources(cursor, conn)

    return jsonify({'status': 'error', 'message': 'Invalid seat ID or amount provided.'})



if __name__ == '__main__':
    app.run(debug=True)
