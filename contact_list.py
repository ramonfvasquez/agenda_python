from tkinter import messagebox
import os
import tkinter as tk
import tkinter.ttk as ttk
import webbrowser

import database

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "")


class ContactList:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Contact List")
        self.root.geometry("1450x830")
        self.root.resizable(False, False)

        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH)

        self.frm_contacts = tk.LabelFrame(self.container, text="Contacts")
        self.frm_contacts.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.NSEW
        )

        self.frm_form = tk.LabelFrame(self.container, text="Add Contact")
        self.frm_form.grid(
            row=1, column=0, padx=10, pady=10, ipadx=5, ipady=5, sticky="new"
        )

        self.frm_buttons = tk.Frame(self.container)
        self.frm_buttons.grid(row=1, column=1, padx=10, pady=10, sticky=tk.EW)

        # ############################## CONTACTS ##############################
        self.tree_contacts = ttk.Treeview(self.frm_contacts, height=25)
        self.tree_contacts.grid(row=0, column=0, padx=5, pady=5)
        self.tree_contacts.bind("<<TreeviewSelect>>", self.enable_buttons)
        self.tree_contacts["columns"] = ["name", "phone", "email", "address"]
        for column in self.tree_contacts["columns"]:
            self.tree_contacts.heading(
                column,
                command=lambda _col=column: self.sort_contacts(_col, False),
            )

        self.tree_contacts.column("#0", width=0, stretch=tk.NO)
        self.tree_contacts.column("name", anchor=tk.CENTER, width=250)
        self.tree_contacts.column("email", anchor=tk.CENTER, width=250)
        self.tree_contacts.column("phone", anchor=tk.CENTER, width=250)
        self.tree_contacts.column("address", anchor=tk.CENTER, width=650)

        self.tree_contacts.heading("#0", text="", anchor=tk.CENTER)
        self.tree_contacts.heading("name", text="Full Name", anchor=tk.CENTER)
        self.tree_contacts.heading("phone", text="Phone", anchor=tk.CENTER)
        self.tree_contacts.heading("email", text="Email", anchor=tk.CENTER)
        self.tree_contacts.heading("address", text="Address", anchor=tk.CENTER)
        self.tree_contacts.focus_set()

        self.tree_scroll = ttk.Scrollbar(
            self.frm_contacts, orient="vertical", command=self.tree_contacts.yview
        )
        self.tree_scroll.grid(row=0, column=1, sticky="nse")

        self.tree_contacts.configure(yscrollcommand=self.tree_scroll.set)

        self.show_contacts()

        # ############################## FORM ##############################

        # ############################## FULL NAME ##############################
        tk.Label(self.frm_form, text="First Name:").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )

        self.first_name = tk.StringVar()
        self.ent_first_name = tk.Entry(
            self.frm_form, width=30, textvariable=self.first_name
        )
        self.ent_first_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_first_name.bind(
            "<Key>", lambda event: self.validate_entry(event, self.ent_first_name)
        )
        self.ent_first_name.bind(
            "<KeyRelease>",
            lambda event: self.validate_entry(event, self.ent_first_name),
        )

        tk.Label(self.frm_form, text="Last Name:").grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.E
        )

        self.last_name = tk.StringVar()
        self.ent_last_name = tk.Entry(
            self.frm_form, width=30, textvariable=self.last_name
        )
        self.ent_last_name.grid(row=0, column=3, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_last_name.bind(
            "<Key>", lambda event: self.validate_entry(event, self.ent_last_name)
        )
        self.ent_last_name.bind(
            "<KeyRelease>", lambda event: self.validate_entry(event, self.ent_last_name)
        )

        # ############################## EMAIL ##############################
        tk.Label(self.frm_form, text="Email:").grid(
            row=0, column=4, padx=5, pady=5, sticky=tk.E
        )

        self.email = tk.StringVar()
        self.ent_email = tk.Entry(self.frm_form, width=30, textvariable=self.email)
        self.ent_email.grid(row=0, column=5, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_email.bind(
            "<Key>",
            lambda event: self.validate_entry(event, self.ent_email, category="email"),
        )
        self.ent_email.bind(
            "<KeyRelease>",
            lambda event: self.validate_entry(event, self.ent_email, category="email"),
        )

        # ############################## PHONE ##############################
        tk.Label(self.frm_form, text="Phone:").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.E
        )

        self.lbl_code = tk.Label(self.frm_form, width=30, bd=1, relief=tk.SUNKEN)
        self.lbl_code.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self.codes = get_countries(BASE_DIR + "/countries.csv")
        self.code = tk.StringVar()
        self.cmb_code = ttk.Combobox(
            self.frm_form,
            textvariable=self.code,
            values=[c[0] for c in self.codes.values()],
            width=10,
            state="readonly",
        )
        self.cmb_code.grid(row=2, column=2, padx=5, pady=5, sticky=tk.NSEW)
        self.cmb_code.bind("<<ComboboxSelected>>", lambda _: self.show_country())

        self.phone = tk.StringVar()
        self.ent_phone = tk.Entry(self.frm_form, textvariable=self.phone, width=30)
        self.ent_phone.grid(row=2, column=3, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_phone.bind(
            "<Key>",
            lambda event: [
                self.validate_entry(event, self.ent_phone, category="number"),
                self.set_phone_defaults(event)
                if not self.cmb_code.get() and not self.cmb_phone_category.get()
                else "",
            ],
        )
        self.ent_phone.bind(
            "<KeyRelease>",
            lambda event: [
                self.validate_entry(event, self.ent_phone, category="number"),
                self.set_phone_defaults(event)
                if not self.cmb_code.get() and not self.cmb_phone_category.get()
                else "",
            ],
        )

        self.phone_category = ("Home", "Mobile", "Work")
        category = tk.StringVar()
        self.cmb_phone_category = ttk.Combobox(
            self.frm_form,
            textvariable=category,
            values=self.phone_category,
            state="readonly",
            width=10,
        )
        self.cmb_phone_category.grid(row=2, column=4, padx=5, pady=5, sticky=tk.NSEW)

        # ############################## ADDRESS ##############################
        tk.Label(self.frm_form, text="Country:").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.E
        )

        self.countries = sorted(
            [k for k in get_countries(BASE_DIR + "/countries.csv").keys()]
        )
        country = tk.StringVar()
        self.cmb_country = ttk.Combobox(
            self.frm_form,
            textvariable=country,
            values=self.countries,
            state="readonly",
            width=30,
        )
        self.cmb_country.grid(row=3, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.cmb_country.bind("<<ComboboxSelected>>", self.enable_provinces)

        self.lbl_province = tk.Label(self.frm_form, text="Province:", state="disabled")
        self.lbl_province.grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)

        self.provinces = get_provinces()
        province = tk.StringVar()
        self.cmb_province = ttk.Combobox(
            self.frm_form,
            textvariable=province,
            values=self.provinces,
            state="disabled",
            width=30,
        )
        self.cmb_province.grid(row=3, column=3, padx=5, pady=5, sticky=tk.NSEW)

        tk.Label(self.frm_form, text="City:").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.E
        )

        self.city = tk.StringVar()
        self.ent_city = tk.Entry(self.frm_form, textvariable=self.city, width=30)
        self.ent_city.grid(row=4, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_city.bind(
            "<Key>",
            lambda event: self.validate_entry(
                event, self.ent_city, category="alphanum"
            ),
        )
        self.ent_city.bind(
            "<KeyRelease>",
            lambda event: self.validate_entry(
                event, self.ent_city, category="alphanum"
            ),
        )

        tk.Label(self.frm_form, text="Street:").grid(
            row=4, column=2, padx=5, pady=5, sticky=tk.E
        )

        self.street = tk.StringVar()
        self.ent_street = tk.Entry(self.frm_form, textvariable=self.street, width=30)
        self.ent_street.grid(row=4, column=3, padx=5, pady=5, sticky=tk.NSEW)
        self.ent_street.bind(
            "<Key>",
            lambda event: self.validate_entry(
                event, self.ent_street, category="alphanum"
            ),
        )
        self.ent_street.bind(
            "<KeyRelease>",
            lambda event: self.validate_entry(
                event, self.ent_street, category="alphanum"
            ),
        )

        tk.Label(self.frm_form, text="Number:").grid(
            row=4, column=4, padx=5, pady=5, sticky=tk.E
        )

        self.house_number = tk.StringVar()
        self.ent_house_number = tk.Entry(
            self.frm_form, textvariable=self.house_number, width=10
        )
        self.ent_house_number.grid(row=4, column=5, padx=5, pady=5, sticky=tk.W)
        self.ent_house_number.bind(
            "<Key>",
            lambda event: self.validate_entry(
                event, self.ent_house_number, category="number"
            ),
        )
        self.ent_house_number.bind(
            "<KeyRelease>",
            lambda event: self.validate_entry(
                event, self.ent_house_number, category="number"
            ),
        )

        # ############################## BUTTONS ##############################
        self.btn_add = tk.Button(
            self.frm_buttons,
            text="Add",
            width=30,
            height=1,
            command=lambda: [
                database.add_contact(self, self.get_contact_data()),
                self.reset_form() if database.completed else "",
            ],
        )
        self.btn_add.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)

        self.btn_update = tk.Button()

        self.btn_view_contact = tk.Button(
            self.frm_buttons,
            text="View Contact",
            state="disabled",
            width=30,
            height=1,
            command=self.win_data,
        )
        self.btn_view_contact.grid(row=1, column=0, padx=5, pady=5, sticky=tk.S)

        self.btn_edit = tk.Button(
            self.frm_buttons,
            text="Edit",
            state="disabled",
            width=30,
            height=1,
            command=self.edit_contact,
        )
        self.btn_edit.grid(row=2, column=0, padx=5, pady=5, sticky=tk.S)

        self.btn_delete = tk.Button(
            self.frm_buttons,
            text="Delete",
            state="disabled",
            width=30,
            height=1,
            command=lambda: [
                database.delete_contact(self, self.tree_contacts),
                self.reset_form(),
            ],
        )
        self.btn_delete.grid(row=3, column=0, padx=5, pady=5, sticky=tk.S)

        self.btn_search = tk.Button(
            self.frm_buttons,
            text="Search",
            width=30,
            height=1,
            command=self.win_search,
        )
        self.btn_search.grid(row=4, column=0, padx=5, pady=5, sticky=tk.S)

        self.btn_reset = tk.Button(
            self.frm_buttons,
            text="Reset Form",
            width=30,
            height=1,
            command=self.reset_form,
        )
        self.btn_reset.grid(row=5, column=0, padx=5, pady=5, sticky=tk.S)

        self.root.mainloop()

    def edit_contact(self):
        """
        Puts all data of the selected contact into their corresponding entries
        and comboboxes; destroys the add-contact button; creates the update-contact
        button; disables the edit-contact button.
        """
        self.btn_add.destroy()
        self.btn_update = tk.Button(
            self.frm_buttons,
            text="Update",
            width=30,
            height=1,
            command=lambda: [
                database.update_contact(self, self.get_contact_data()),
                self.reset_form() if database.completed else "",
            ],
        )

        self.btn_update.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)
        self.frm_form["text"] = "Edit Contact"
        self.btn_edit["state"] = "disabled"

        contact = database.search_contact(id=self.tree_contacts.focus())[0]

        self.first_name.set(contact[1])
        self.last_name.set(contact[2])
        self.email.set(contact[6])
        self.code.set(contact[3])
        self.phone.set(contact[4])
        self.cmb_phone_category.set(contact[5])
        self.cmb_country.set(contact[11])
        self.cmb_province.set(contact[10])
        self.city.set(contact[9])
        self.street.set(contact[7])
        self.house_number.set(contact[8])

        self.enable_provinces("")
        self.show_country()

    def enable_buttons(self, event):
        """
        Enables view-contact, edit-contact, and delete-contact buttons when
        selecting a contact.
        """
        if self.tree_contacts.selection() != ():
            self.btn_view_contact["state"] = "normal"
            self.btn_edit["state"] = "normal"
            self.btn_delete["state"] = "normal"
        else:
            self.btn_view_contact["state"] = "disabled"
            self.btn_edit["state"] = "disabled"
            self.btn_delete["state"] = "disabled"

    def enable_provinces(self, event):
        # Enables province combobox if the selected country is Argentina
        if self.cmb_country.get() == "Argentina":
            self.lbl_province["state"] = "normal"
            self.cmb_province["state"] = "readonly"
        else:
            self.lbl_province["state"] = "disabled"
            self.cmb_province["state"] = "disabled"
            self.cmb_province.set("")

    def get_contact_data(self):
        return [
            self.first_name.get(),
            self.last_name.get(),
            self.code.get() if self.phone.get() else "",
            self.phone.get() if self.phone.get() else "",
            self.cmb_phone_category.get() if self.phone.get() else "",
            self.email.get(),
            self.street.get(),
            self.house_number.get()
            if self.house_number.get() and self.street.get()
            else "",
            self.city.get(),
            self.cmb_province.get(),
            self.cmb_country.get(),
            self.tree_contacts.focus(),
        ]

    def reset_form(self):
        self.lbl_code.config(text="", image="")
        self.cmb_code.set("")
        self.cmb_phone_category.set("")
        self.cmb_country.set("")
        self.lbl_province["state"] = "disabled"
        self.cmb_province.set("")
        self.cmb_province["state"] = "disabled"

        for widget in self.frm_form.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

        self.ent_first_name.focus_set()
        self.tree_contacts.selection_remove()

        if self.btn_add:
            self.btn_update.destroy()

            self.btn_add = tk.Button(
                self.frm_buttons,
                text="Add",
                width=30,
                height=1,
                command=lambda: [
                    database.add_contact(self, self.get_contact_data()),
                    self.reset_form() if database.completed else "",
                ],
            )
            self.btn_add.grid(row=0, column=0, padx=5, pady=5, sticky=tk.S)

    def set_phone_defaults(self, event):
        self.cmb_code.set("+54")
        self.show_country()
        self.cmb_phone_category.set("Mobile")

    def show_contacts(self):
        # Fills the treeview with the contacts in the DB
        db = database.connection("contact_list")
        cur = db.cursor()
        sql = "SELECT * FROM contact ORDER BY first_name ASC"

        cur.execute(sql)
        res = cur.fetchall()

        self.tree_contacts.delete(*self.tree_contacts.get_children())

        for i, res in enumerate(res):
            self.tree_contacts.insert(
                parent="",
                index=i,
                iid=res[0],
                values=(
                    res[1] + (" " if res[2] else "") + res[2],
                    get_phone(res[3], res[4], res[5]),
                    res[6],
                    ", ".join(get_address(res)),
                ),
            )

    def show_country(self):
        # Shows a flag and the country name depending on the selected country code
        self.lbl_code["text"] = " " + "".join(
            [k for k, v in self.codes.items() if v[0] == self.cmb_code.get()]
        )
        self.lbl_code["compound"] = tk.LEFT
        self.lbl_code["image"] = [
            v[1] for v in self.codes.values() if v[0] == self.cmb_code.get()
        ]

    def sort_contacts(self, column, reverse):
        list = [
            (self.tree_contacts.set(k, column), k)
            for k in self.tree_contacts.get_children("")
        ]
        list.sort(reverse=reverse)

        # Rearranges items in sorted positions
        for index, (val, k) in enumerate(list):
            self.tree_contacts.move(k, "", index)

        # Reverses sort next time the column is clicked
        self.tree_contacts.heading(
            column, command=lambda _col=column: self.sort_contacts(_col, not reverse)
        )

    def validate_entry(self, key, entry, category="text"):
        """
        Validates each entry's text according to these categories: text,
        email, number, or alphanumeric. When typing an incorrect value,
        the text turns red.
        """
        dato = entry.get()

        if category == "text":
            res = database.is_invalid_text(dato)
        elif category == "email":
            res = not database.is_valid_email(dato)
        elif category == "number":
            res = database.is_invalid_number(dato)
        elif category == "alphanum":
            res = database.is_invalid_alphanumeric(dato)

        if res:
            entry["fg"] = "red"
        else:
            entry["fg"] = "black"

    def win_data(self):
        # Opens the contact-data window
        win = WinData(self.tree_contacts.focus(), master=self.root)

        win.transient(self.root)
        win.grab_set()
        self.root.wait_window(win)

    def win_search(self):
        # Opens the search window
        win = WinSearch(self.tree_contacts, master=self.root)


class WinData(tk.Toplevel):
    def __init__(self, id, master=None, *args, **kwargs):
        tk.Toplevel.__init__(self, master=master)
        self.title("Contact Info")
        self.geometry("700x170")

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH)

        contact = database.search_contact(id=id)[0]

        tk.Label(self.container, text="Full Name:", font="Default 11 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )
        lbl_name = tk.Label(self.container, text=contact[1] + " " + contact[2])
        lbl_name.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.container, text="Phone:", font="Default 11 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.E
        )
        lbl_phone = tk.Label(
            self.container,
            text=get_phone(contact[3], contact[4], contact[5]),
        )
        lbl_phone.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.container, text="Email:", font="Default 11 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.E
        )
        lbl_email = tk.Label(self.container, text=contact[6])
        lbl_email.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.container, text="Address:", font="Default 11 bold").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.E
        )

        lbl_address = tk.Label(
            self.container,
            text=", ".join(get_address(contact)),
            fg="blue",
            font="Default 11 underline",
            anchor=tk.W,
        )
        lbl_address.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        lbl_address.bind(
            "<Button-1>",
            lambda e: self.open_google_maps(
                "https://www.google.com/maps/place/" + lbl_address["text"]
            ),
        )

    def open_google_maps(self, url):
        webbrowser.open(url)


class WinSearch(tk.Toplevel):
    def __init__(self, treeview, master=None, *args, **kwargs):
        tk.Toplevel.__init__(self, master=master)
        self.title("Contact Info")
        self.geometry("800x50")

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, padx=5, pady=5)

        tk.Label(self.container, text="First Name:").grid(row=0, column=0)

        self.ent_first_name = tk.Entry(self.container, width=30)
        self.ent_first_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.container, text="Last Name:").grid(row=0, column=2)

        self.ent_last_name = tk.Entry(self.container, width=30)
        self.ent_last_name.grid(row=0, column=3, padx=5, pady=5)

        self.btn_search = tk.Button(
            self.container, text="Search", command=self.search_contact
        )
        self.btn_search.grid(row=0, column=4, padx=5, pady=5)

        self.treeview = treeview

    def search_contact(self):
        try:
            res = database.search_contact(
                first_name=(self.ent_first_name.get(),),
                last_name=(self.ent_last_name.get(),),
            )[0][0]
            self.treeview.selection_set(res)
            self.treeview.focus(res)
        except:
            messagebox.showinfo("Not Found", "Contact not found!")


def get_address(data):  # Fills a list with the full address data
    address = []
    if data[7]:
        address.append(data[7] + (" " + str(data[8]) if data[8] else ""))
    if data[9]:
        address.append(data[9])
    if data[10]:
        address.append(data[10])
    if data[11]:
        address.append(data[11])

    return address


def get_countries(file_name):
    # Gets the countries and the country codes from countries.csv
    dic_flags = {}

    file = open(file_name, "r", encoding="utf8")
    lines = file.readlines()

    for line in lines:
        line = line.replace("\n", "")
        line = line.split(",")
        dic_flags[line[0]] = [
            line[1],
            tk.PhotoImage(file=STATIC_ROOT + "flags/" + line[2]),
        ]

    return dic_flags


def get_provinces():
    return [
        "Buenos Aires",
        "CABA",
        "Catamarca",
        "Chaco",
        "Chubut",
        "Córdoba",
        "Corrientes",
        "Formosa",
        "Jujuy",
        "La Pampa",
        "La Rioja",
        "Mendoza",
        "Misiones",
        "Neuquén",
        "Río Negro",
        "Salta",
        "San Luis",
        "San Juan",
        "Santa Cruz",
        "Santa Fe",
        "Santiago del Estero",
        "Tierra del Fuego",
        "Tucumán",
        "Ushuahia",
    ]


def get_phone(code, phone, phone_category):  # Returns a string with the full phone data
    return (
        ("(" if phone else "")
        + code
        + (") " if phone else "")
        + phone
        + (" [" if phone else "")
        + phone_category
        + ("]" if phone else "")
    )


def main():
    database.create_db()
    database.create_table()
    app = ContactList()


if __name__ == "__main__":
    main()
