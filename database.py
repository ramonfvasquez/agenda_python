import mysql.connector
import re
import tkinter as tk
from tkinter import messagebox

completed = False


def connection(database=None):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="R+D@11",
        database=database,
        auth_plugin="mysql_native_password",
    )


def create_db():
    db = connection()
    try:
        cur = db.cursor()
        sql = "CREATE DATABASE contact_list;"

        cur.execute(sql)

        print("The DB has been successfully created! :)")
    except:
        print()


def create_table():
    db = connection("contact_list")
    try:
        cur = db.cursor()
        sql = """
            CREATE TABLE contact (id INT(10) NOT NULL PRIMARY KEY AUTO_INCREMENT, 
            first_name VARCHAR(50) COLLATE utf8_spanish2_ci NOT NULL, last_name 
            VARCHAR(50) COLLATE utf8_spanish2_ci, country_code VARCHAR(10), 
            phone VARCHAR(20), phone_category VARCHAR(10), email VARCHAR(50), 
            street VARCHAR(50) COLLATE utf8_spanish2_ci, house_number VARCHAR(10), city 
            VARCHAR(50) COLLATE utf8_spanish2_ci, province VARCHAR(50) COLLATE 
            utf8_spanish2_ci, country VARCHAR(50) COLLATE utf8_spanish2_ci);
            """

        cur.execute(sql)

        print("The table has been successfully created! :)")
    except:
        print()


def add_contact(parent, data):
    global completed

    data.remove(data[-1])

    db = connection("contact_list")
    cur = db.cursor()
    sql = """
        INSERT INTO contact (first_name, last_name, country_code, phone, 
        phone_category, email, street, house_number, city, province, country) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    invalid = get_invalid_data(data)

    if data[0]:
        if not contact_exists(data[0], data[1]):
            if invalid:
                messagebox.showerror(
                    "Invalid Values",
                    "The following fields have invalid values: "
                    + ", ".join(invalid)
                    + ".",
                )

                completed = False
            else:
                cur.execute(sql, data)
                db.commit()

                parent.show_contacts()

                messagebox.showinfo(
                    "Contact Created",
                    "%s%s%s has been successfully added!"
                    % (data[0], " " if data[1] else "", data[1]),
                )

                completed = True
        else:
            messagebox.showwarning(
                "Existing Contact",
                "%s%s%s is already a contact!"
                % (data[0], " " if data[1] else "", data[1]),
            )

            completed = False
    else:
        messagebox.showerror("Name Required", "You can't create a nameless contact!")

        completed = False

    db.close()


def update_contact(parent, data):
    global completed

    db = connection("contact_list")
    cur = db.cursor()
    sql = """
        UPDATE contact SET first_name = %s, last_name = %s, country_code = %s, 
        phone = %s, phone_category = %s, email = %s, street = %s, house_number = %s, 
        city = %s, province = %s, country = %s WHERE id = %s;
        """
    invalid = get_invalid_data(data)

    if data[0]:
        if invalid:
            messagebox.showerror(
                "Invalid Values",
                "The following fields have invalid values: " + ", ".join(invalid) + ".",
            )

            completed = False
        else:
            cur.execute(sql, data)
            db.commit()

            parent.show_contacts()

            messagebox.showinfo(
                "Contact Updated",
                "%s%s%s's data has been updated!"
                % (data[0], " " if data[1] else "", data[1]),
            )

            completed = True

            parent.btn_update.destroy()

            parent.btn_add = tk.Button(
                parent.frm_buttons,
                text="Add",
                width=30,
                height=1,
                command=lambda: [
                    add_contact(parent, parent.get_contact_data()),
                    parent.reset_form() if completed else "",
                ],
            )
            parent.btn_add.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)

            parent.frm_form["text"] = "Add Contact"
    else:
        messagebox.showerror("Name Required", "You can't update a nameless contact!")

    db.close()


def delete_contact(parent, treeview):
    # Sets the instructin to delete the selected contact
    db = connection("contact_list")
    cur = db.cursor()
    sql_1 = "DELETE FROM contact WHERE id = %s;"
    id = treeview.focus()
    dato = (id,)

    # Gets first and last names to fill the messagebox
    sql_2 = "SELECT first_name, last_name FROM contact WHERE id = %s;    "
    cur.execute(sql_2, dato)
    res = cur.fetchall()
    first = res[0][0]
    last = res[0][1]

    answer = messagebox.askyesno(
        "Delete Contact",
        "Are you sure you want to delete %s%s%s?" % (first, " " if last else "", last),
    )

    if answer:
        cur.execute(sql_1, dato)
        db.commit()
        parent.show_contacts()

    db.close()


def search_contact(**kwargs):
    db = connection("contact_list")
    data = ()
    sql = ""

    cur = db.cursor()

    for key in kwargs:
        if key == "first_name" or key == "last_name":
            if isinstance(kwargs["first_name"], tuple) or isinstance(
                kwargs["last_name"], tuple
            ):
                if kwargs["first_name"] != ("",) and kwargs["last_name"] == ("",):
                    sql = "SELECT * FROM contact WHERE first_name = %s;"
                    data = (kwargs["first_name"][0],)
                elif kwargs["first_name"] == ("",) and kwargs["last_name"] != ("",):
                    sql = "SELECT * FROM contact WHERE last_name = %s;"
                    data = (kwargs["last_name"][0],)
                elif kwargs["first_name"] != ("",) and kwargs["last_name"] != ("",):
                    sql = "SELECT * FROM contact WHERE first_name = %s AND last_name = %s;"
                    data = (kwargs["first_name"][0], kwargs["last_name"][0])
            else:
                sql = "SELECT * FROM contact WHERE first_name = %s AND last_name = %s;"
                data = (kwargs["first_name"], kwargs["last_name"])
        elif key == "id":
            sql = "SELECT * FROM contact WHERE id = %s"
            data = (kwargs["id"],)

    cur.execute(sql, data)
    res = cur.fetchall()

    db.close()

    return res


def get_invalid_data(data):
    invalid = []

    if is_invalid_text(data[0]):
        invalid.append("first name")
    if is_invalid_text(data[1]):
        invalid.append("last name")
    if data[5] and not is_valid_email(data[5]):
        invalid.append("email")
    if is_invalid_number(data[3]):
        invalid.append("phone")
    if is_invalid_alphanumeric(data[8]):
        invalid.append("city")
    if is_invalid_alphanumeric(data[6]):
        invalid.append("street")
    if is_invalid_number(data[7]):
        invalid.append("house number")

    return invalid


def contact_exists(first_name, last_name):
    return search_contact(first_name=first_name, last_name=last_name)


def is_invalid_text(data):
    return re.search(r"[^A-Za-zÁáÉéÍíÓóÚú \'\.-]+", data)


def is_valid_email(data):
    return re.search(r"([A-Za-z0-9_\.]+@[A-Za-z0-9_]+(?:\.[a-z]+)+)", data)


def is_invalid_number(data):
    return re.search(r"[^0-9]+", data)


def is_invalid_alphanumeric(data):
    return re.search(r"[^A-Za-z0-9ÁáÉéÍíÓóÚú \'\.-]+", data)
