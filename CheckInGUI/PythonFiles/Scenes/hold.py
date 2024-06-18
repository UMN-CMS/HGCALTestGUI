
            # Adds the title to the Summary Frame
            self.title = tk.Label(
                    self.frame, 
                    fg='#0d0d0d', 
                    text = "This Board has already been Checked In",
                    font=('Arial',18,'bold')
                    )
            self.title.grid(row= 0, column= 1, pady = 20)
                

            # Adds Board full id to the SummaryFrame
            self.id = tk.Label(
                    self.frame, 
                    fg='#0d0d0d', 
                    text = "Full ID:" + str(self.data_holder.data_dict['current_full_ID']),
                    font=('Arial',14,'bold')
                    )
            self.id.grid(row= 1, column= 1, pady = 20)

            green_check = Image.open("{}/Images/GreenCheckMark.png".format(PythonFiles.__path__[0]))
            green_check = green_check.resize((75, 75), Image.LANCZOS)
            green_check = iTK.PhotoImage(green_check)

            redx = Image.open('{}//Images/RedX.png'.format(PythonFiles.__path__[0]))
            redx = redx.resize((75, 75), Image.LANCZOS)
            redx = iTK.PhotoImage(redx)
            try:
                if self.data_holder.data_dict['test_names']:
                    res_dict = {}
                    for n in self.data_holder.data_dict['test_names']:
                        res_dict[n] = []
                    for idx,el in enumerate(self.data_holder.data_dict['prev_results']):
                        res_dict[el[0]] = el[1]

                    for idx,el in enumerate(res_dict.keys()):
                        self.lbl_res = tk.Label(
                                self.frame,
                                text = str(el) + ': ',
                                font=('Arial',14)
                                )
                        self.lbl_res.grid(row=idx+2, column=1)
                        if res_dict[el] == 'Passed':
                            self.lbl_img = tk.Label(
                                    self.frame,
                                    image = green_check,
                                    width=75,
                                    height=75,
                                    font=('Arial',14)
                                    )
                            self.lbl_img.image=green_check
                            self.lbl_img.grid(row=idx+2, column=2)
                        else:
                            self.lbl_img = tk.Label(
                                    self.frame,
                                    image = redx,
                                    width=75,
                                    height=75,
                                    font=('Arial',14)
                                    )
                            self.lbl_img.image=redx
                            self.lbl_img.grid(row=idx+2, column=2)
                else:
                    self.lbl_res = tk.Label(
                            self.frame,
                            text = str(self.data_holder.data_dict['prev_results']),
                            font=('Arial',14)
                            )
                    self.lbl_res.grid(row=2, column=1)

            except Exception as e:
                print(e)
                self.lbl_err = tk.Label(
                        self, 
                        text = "Some other error occured and Board was not entered. See logs for more info.",
                        font=('Arial', 14) 
                        )
                self.lbl_err.grid(column = 1, row = 2, pady = 10) 
