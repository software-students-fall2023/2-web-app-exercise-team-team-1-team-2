
let allImages = document.querySelectorAll(".img-num");
let mainImage = document.querySelector(".img-5-inside");

function firstImage() {
	mainImage.srcset = "gal-images/bed-375.jpg 375w, gal-images/bed-900.jpg 900w";
}
function secondImage() {
	mainImage.srcset = "gal-images/deer-375.jpg 375w, gal-images/deer-900.jpg 900w";
}
function thirdImage() {
	mainImage.srcset = "gal-images/box-375.jpg 375w, gal-images/box-900.jpg 900w";
}
function fourthImage() {
	mainImage.srcset = "gal-images/sunset-375.jpg 375w, gal-images/sunset-900.jpg 900w";
}
function fifthImage() {
	mainImage.srcset = "gal-images/mom-375.jpg 375w, gal-images/mom-900.jpg 900w";
}

allImages[0].addEventListener('click', firstImage);
allImages[1].addEventListener('click', secondImage);
allImages[2].addEventListener('click', thirdImage);
allImages[3].addEventListener('click', fourthImage);
allImages[4].addEventListener('click', fifthImage);
