function showLogin(){
    document.querySelector('.login-wrapper').style.display = "flex"
    document.querySelector('.signup-wrapper').style.display = "none"
}

function closeLogin(){
    document.querySelector('.login-wrapper').style.display = "none"
}


function showSignup(){
    document.querySelector('.login-wrapper').style.display = "none"
    document.querySelector('.signup-wrapper').style.display = "flex"
}

function closeSignup(){
    document.querySelector('.signup-wrapper').style.display = "none"
}


function showSignupCharity(){
    document.querySelector('.login-wrapper').style.display = "none"
    document.querySelector('.signup-wrapper').style.display = "none"
    document.querySelector('.signup-wrapper-charity').style.display = "flex"
}

function closeSignupCharity(){
    document.querySelector('.signup-wrapper-charity').style.display = "none"
}

function setProfilePic(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // document.querySelector('.profile-pic').style.display = "flex"
            // document.querySelector('.profile-pic-name').textContent = input.value.replace("C:\\fakepath\\","")
            $('.profile-pic')
                .attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }

  
}

function setProfilePic2(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // document.querySelector('.profile-pic').style.display = "flex"
            // document.querySelector('.profile-pic-name').textContent = input.value.replace("C:\\fakepath\\","")
            $('.profile-pic2')
                .attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }

  
}