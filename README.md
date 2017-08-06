# blood-donation-platform



+=====================================================+
|                        User                         |
+=====================================================+
| email (email field)                                 |
+-----------------------------------------------------+
| password (password field)                           |
+-----------------------------------------------------+
| firstName (string)                                  |
+-----------------------------------------------------+
| lastName (string)                                   |
+-----------------------------------------------------+
| phone (string)                                      |
+-----------------------------------------------------+
| address { country, street, city, zipCode } (object) |
+-----------------------------------------------------+
| birthDate (date)                                    |
+-----------------------------------------------------+
| bloodType { A+, A-, B+, .... } (enum)               |
+-----------------------------------------------------+
| emailNotification (boolean)                         |
+-----------------------------------------------------+
| smsNotification (boolean)                           |
+-----------------------------------------------------+



+========================================+
|             bloodDonation              |
+========================================+
| createdAt (dateTime)                   |
+----------------------------------------+
| applicant (User)                       |
+----------------------------------------+
| deadline (dateTime)                    |
+----------------------------------------+
| description (String)                   |
+----------------------------------------+
| city (string, default : from profile)  |
+----------------------------------------+
| phone (string, default : from profile) |
+----------------------------------------+
| status (string)                        |
+----------------------------------------+
