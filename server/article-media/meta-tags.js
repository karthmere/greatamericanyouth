const url = window.location.href;

const urlArr = url.split("/");
const urlName = urlArr[urlArr.length-1];

const apiUrl = "https://greatamericanyouth.com/api/article-meta";
// Make the API call with the urlName parameter
fetch(`${apiUrl}?urlName=${urlName}`)
  .then(response => response.json())
     .then(data => {
             const { title, description, thumbnail } = data;

                     document.title = title;
	             const headElement = document.querySelector('head');
                     //document.querySelector('meta[property="description"]').setAttribute("content", description);
                     //document.querySelector('meta[property="og:title"]').setAttribute("content", title);
                     //document.querySelector('meta[property="og:description"]').setAttribute("content", description);
                     //document.querySelector('meta[property="og:image"]').setAttribute("content", thumbnail);

	     // Create the og:image meta element
	             const ogImage = document.createElement('meta');
	             ogImage.setAttribute('property', 'og:image');
	             ogImage.setAttribute('content', thumbnail);
	             const ogTitle = document.createElement('meta');
	             ogTitle.setAttribute('property', 'og:title');
	             ogTitle.setAttribute('content', thumbnail);
	             const ogDescription = document.createElement('meta');
	             ogDescription.setAttribute('property', 'og:description');
	             ogDescription.setAttribute('content', description);
	             const descriptionElement= document.createElement('meta');
	             descriptionElement.setAttribute('property', 'description');
	             descriptionElement.setAttribute('content', description);

	     // headElement.appendChild(ogImageElement);
	     //
	     // // Create the og:description meta element
	     // const ogDescriptionElement = document.createElement('meta');
	     // ogDescriptionElement.setAttribute('property', 'og:description');
	     // ogDescriptionElement.setAttribute('content', 'This is the Open Graph description');
	     // headElement.appendChild(ogDescriptionElement);
	     //
	     // // Create the description meta element
	     // const descriptionElement = document.createElement('meta');
	     // descriptionElement.setAttribute('name', 'description');
	     // descriptionElement.setAttribute('content', 'This is the regular description');
	     // headElement.appendChild(descriptionElement);
	     //
	     // // Create the og:title meta element
	     // const ogTitleElement = document.createElement('meta');
	     // ogTitleElement.setAttribute('property', 'og:title');
	     // ogTitleElement.setAttribute('content', 'This is the Open Graph title');
	     // headElement.appendChild(ogTitleElement);
              })
                  .catch(error => console.error(error));
