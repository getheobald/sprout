function plantInfoPopup(clickedPlant)
{
  let plantInfo = clickedPlant.querySelector('.plantInfo');
  closeAllPopups(plantInfo);
  plantInfo.classList.toggle('show');
}

//close all popups before opening a new one
/*got this from here:
https://stackoverflow.com/questions/39428025/how-to-make-only-1-popup-open-at-a-time
I know I basically used all their code but could not figure out another way to do it*/
function closeAllPopups(plantInfo)
{
  var allPopups = document.getElementsByClassName('actual_popup');
  for (i = 0; i < allPopups.length; i++)
  {
    if (allPopups[i] != plantInfo)
    {
      allPopups[i].classList.remove('show');
    }
  }
}
