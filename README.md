[README.md](https://github.com/user-attachments/files/24816275/README.md)
## Names of all members in our team
- Victoria Timofeev
- Christine Le
- Ryan Soe

## The password for user "grader" on your Apache server (TODO)
- UPDATE: If you use an SSH key for your **root** user, you will need to use an SSH key for your **grader** account, which means that we will need the **private key** for this grader account (along with the passphrase for this private key if there is one). **INCLUDE THIS SSH KEY AND (if applicable) PASSPHRASE ALONG WITH THE PASSWORD FOR THE GRADER ACCOUNT** in your submission.
- **Test logging** into the grader account before submission. If we cannot log into this account, we cannot grade your homework and there may be a penalty. Please indicate all log in information for the TAs carefully.

## Link to our site, which has:
https://cse135vrc.site

- homepage with team member info and homework links
- about pages for each team member
- favicon
- robots.txt
- hw1/hello.php
- hw1/report.html

## Details of Github auto deploy setup (TODO)


## Username/password info for logging into the site
Username: ryan  
Password: ryan

Username: victoria  
Password: victoria

Username: christine  
Password: christine

Username: grader  
Password: grader

## Summary of changes to HTML file in DevTools after compression
After implementing compressions to our site, we observed that the file size for our main page got compressed from 0.6 kB to 0.5 kB.

## Summary of removing 'server' header

First, I ran this:
```
sudo a2enmod headers
sudo systemctl restart apache2
```
This is to install mod_headers which is used to change the server header.

Then, I added this to the apache config file:
```
<IfModule mod_headers.c>
    Header always set Server "CSE135 Server"
    Header unset X-Powered-By
</IfModule>
```
This ensures that our custom server header always overrides the Apache default server header.
