
let posts = JSON.parse(localStorage.getItem('posts')) || [];

function updatePostsView() {
    const filterWordLength = document.getElementById('exactWordLengthFilter').value;
    const filterLanguage = document.getElementById('filterLanguage').value;
    const sortOption = document.getElementById('sortOption').value;
    const searchInput = document.getElementById('searchInput').value.toLowerCase().trim();
    const itemsPerPage = parseInt(document.getElementById('itemsPerPage').value);

    let filteredPosts = posts.filter(post => {
        return (filterWordLength === 'all' || (filterWordLength === '13+' ? post.content.length > 12 : post.content.length == filterWordLength)) &&
               (filterLanguage === 'all' || post.language === filterLanguage) &&
               (!searchInput || post.hint.toLowerCase().includes(searchInput));
    });

    switch (sortOption) {
        case 'recent':
            filteredPosts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
            break;
        case 'clicks':
            filteredPosts.sort((a, b) => b.clicks - a.clicks);
            break;
        case 'random':
            filteredPosts = filteredPosts.sort(() => Math.random() - 0.5);
            break;
        case 'wrongAttempts':
            filteredPosts.sort((a, b) => b.wrongAttempts - a.wrongAttempts);
            break;
    }

    renderPagination(filteredPosts, itemsPerPage);
    // After rendering the posts, reinitialize all Swipers
    initializeAllSwipers();
        // Call to renderFilteredPosts or directly within updatePostsView
    document.querySelectorAll('.input-group input').forEach(input => {
        input.removeEventListener('keypress', handleKeyPress); // Prevent multiple bindings
        input.addEventListener('keypress', handleKeyPress);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadPosts(); // Load posts when the document is ready
    showTab('active'); // Show the active tab initially
});

// Function to initialize Swiper for a specific post ID
function initializeSwiper(postId) {
    if (postId) {
        new Swiper('#swiper_' + postId, {
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            loop: true,
        });
    }
}

// Function to initialize Swipers for all posts
function initializeAllSwipers() {
    posts.forEach(post => {
        initializeSwiper(post.id);
    });
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        const postId = event.target.id.split('_')[1];
        checkInput(postId);
        event.preventDefault(); // prevent form submission
    }
}

function renderPagination(posts, itemsPerPage) {
    const paginationContainer = document.getElementById('pagination');
    const totalPages = Math.ceil(posts.length / itemsPerPage);
    let currentPage = 1;

    paginationContainer.innerHTML = '';
    for (let page = 1; page <= totalPages; page++) {
        const button = document.createElement('button');
        button.textContent = page;
        button.onclick = () => renderPage(posts, page, itemsPerPage);
        paginationContainer.appendChild(button);
    }

    renderPage(posts, currentPage, itemsPerPage);
}

function renderPage(posts, page, itemsPerPage) {
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pagePosts = posts.slice(start, end);

    const activePostsContainer = document.getElementById('postsContainer');
    const completedPostsContainer = document.getElementById('completedPostsContainer');
    renderFilteredPosts(pagePosts.filter(post => post.status === 'active'), activePostsContainer, 'Active');
    renderFilteredPosts(pagePosts.filter(post => post.status === 'completed'), completedPostsContainer, 'Completed');
}
function checkSidebarExpansion() {
    const filtersVisible = document.getElementById('filtersContainer').classList.contains('show');
    const loginVisible = document.getElementById('loginContainer').classList.contains('show');
    const sidebar = document.getElementById('sidebar');


    if (filtersVisible || loginVisible) {
        sidebar.classList.add('expanded');
    } else {
        sidebar.classList.remove('expanded');
    }
}

function toggleFilters() {
    const filtersContainer = document.getElementById('filtersContainer');
    filtersContainer.classList.toggle('show');
    checkSidebarExpansion();
}

function toggleLogin() {
    const loginContainer = document.getElementById('loginContainer');
    loginContainer.classList.toggle('show');
    checkSidebarExpansion();
}

function searchPosts() {
    const keyword = document.getElementById('searchInput').value.trim().toLowerCase();

    // If no keyword is provided, reset the view to show all posts
    if (!keyword) {
        updatePostsView(); // Calls the function that refreshes the entire view with all posts
        return;
    }

    const activePostsContainer = document.getElementById('postsContainer');
    const completedPostsContainer = document.getElementById('completedPostsContainer');

    // Filtering both active and completed posts based on the hint containing the keyword
    const filteredActivePosts = posts.filter(post => post.status === 'active' && post.hint.toLowerCase().includes(keyword));
    const filteredCompletedPosts = posts.filter(post => post.status === 'completed' && post.hint.toLowerCase().includes(keyword));

    // Display results or indicate no matches
    renderFilteredPosts(filteredActivePosts, activePostsContainer, 'Active');
    renderFilteredPosts(filteredCompletedPosts, completedPostsContainer, 'Completed');

    // Filtered search applying all active filter settings
    updatePostsView(keyword);
}

function renderFilteredPosts(filteredPosts, container, status) {
    container.innerHTML = `<h2>${status} Posts</h2>`;
    if (filteredPosts.length === 0) {
        container.innerHTML += '<p>No posts found matching your criteria.</p>';
    } else {
        filteredPosts.forEach(post => {
            const elapsedTime = getElapsedTime(post.timestamp);
            const postElement = document.createElement('div');
            postElement.className = 'post';
            postElement.innerHTML = createPostHTML(post, elapsedTime);
            container.appendChild(postElement);
        });
    }
}


function toggleDropdown(postId) {
    const postContainer = document.querySelector(`#post_${postId}`);
    const dropdown = document.getElementById(`dropdown_${postId}`);
    const isVisible = dropdown.style.display === 'block';

    // Toggle the display of the dropdown
    dropdown.style.display = isVisible ? 'none' : 'block';

    // Toggle the selected class on the post container
    if (isVisible) {
        postContainer.classList.remove('selected');
    } else {
        postContainer.classList.add('selected');
    }
}
function toggleDropdownMenu(postId) {
    const dropdownMenu = document.getElementById(`dropdown_${postId}`);
    dropdownMenu.style.display = dropdownMenu.style.display === 'none' ? 'block' : 'none';
}

function toggleHint(postId) {
    const hintElement = document.getElementById(`hint_${postId}`);
    if (hintElement.style.display === 'none') {
        hintElement.style.display = 'block';
        incrementClickCount(postId); // Increment click count when showing hint
    } else {
        hintElement.style.display = 'none';
    }
}

function incrementClickCount(postId) {
    const post = posts.find(p => p.id === postId);
    if (post.clicks === 0) {
        post.clicks = 1;
    } else {
        post.clicks += 0.5;
    }
    document.getElementById(`clicks_${postId}`).textContent = `Clicks: ${post.clicks}`;
    savePosts();
    updatePostsView();
}

function deletePost(postId) {
    posts = posts.filter(p => p.id !== postId);
    savePosts();
    updatePostsView();
}

function editPost(postId) {
    const post = posts.find(p => p.id === postId);
    const newContent = prompt('Enter the new content for the post:', post.content);
    if (newContent !== null) {
        post.content = newContent;
        savePosts();
        updatePostsView();
    }
}

function checkInput(postId) {
    const post = posts.find(p => p.id === postId);
    const input = document.getElementById(`input_${postId}`).value;

    // Check if the user's input matches the correct content
    if (input.trim() === post.content) {
        post.status = 'completed';  // Mark the post as completed
        alert('Correct! The post has been completed.');
        savePosts();  // Save changes to localStorage
        updatePostsView();  // Refresh the view to reflect changes
    } else {
        post.attempts--;  // Decrement the attempts

        // Provide feedback based on the remaining number of attempts
        if (post.attempts > 0) {
            alert(`Incorrect. You have ${post.attempts} attempts remaining.`);
        } else {
            post.wrongAttempts++;  // Increment the wrong attempts counter if attempts are exhausted
            alert('No attempts left. Please try another post.');
            post.attempts = 4;  // Optionally reset attempts for a new try
            document.getElementById(`wrongAttempts_${postId}`).innerText = post.wrongAttempts; // Update wrong attempts in the UI
        }

        // Update UI elements based on remaining attempts
        document.getElementById(`input_${postId}`).disabled = (post.attempts === 0);
        document.getElementById(`input_${postId}`).style.borderColor = (post.attempts === 0 ? 'red' : 'initial');

        savePosts();  // Save changes to local storage
        updatePostsView();  // Refresh the view to show updated attempt counts and statuses
    }
}

function inputChecking(postId) {
    const post = posts.find(p => p.id === postId);
    const inputValue = prompt('Enter input to check:');
    if (inputValue === post.content) {
        post.status = 'completed'; // Move to completed posts
        savePosts();
    } else {
        post.attempts--;
        if (post.attempts === 0) {
            const hintElement = document.getElementById(`hint_${postId}`);
            hintElement.innerHTML += '<br><input type="checkbox" style="background-color: red;" disabled>';
        }
        savePosts();
    }
    updatePostsView();
}

function showTab(status) {
    const activeContainer = document.getElementById('postsContainer');
    const completedContainer = document.getElementById('completedPostsContainer');
    const activeBtn = document.querySelector('.tab-button:first-child');
    const completedBtn = document.querySelector('.tab-button:last-child');

    if (status === 'active') {
        activeContainer.style.display = 'block';
        completedContainer.style.display = 'none';
        activeBtn.classList.add('active');
        completedBtn.classList.remove('active');
    } else {
        completedContainer.style.display = 'block';
        activeContainer.style.display = 'none';
        completedBtn.classList.add('active');
        activeBtn.classList.remove('active');
    }
    updatePostsView(); // Render posts based on the selected tab and filter
}

function getElapsedTime(timestamp) {
    const now = new Date();
    const elapsed = now - new Date(timestamp);
    const minutes = Math.floor(elapsed / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days} days ago`;
    if (hours > 0) return `${hours} hours ago`;
    if (minutes > 0) return `${minutes} minutes ago`;
    return 'Just now';
}

function toggleLike(postId) {
    const post = posts.find(p => p.id === postId);
    const likeButton = document.getElementById(`likeButton_${post.id}`);

    if (!post.liked) {  // Check if the post has not been liked yet
        post.clicks++;  // Increment the like counter
        post.liked = true;  // Mark the post as liked
    } else {
        post.clicks--;  // Decrement the like counter if unliking
        post.liked = false; // Mark as not liked
    }

    likeButton.innerHTML = `&#10084; ${post.clicks} Likes`; // Update the button text to show current number of likes
    savePosts();  // Save the updated state to local storage
    updatePostsView();  // Refresh the view to show updated like counts and statuses
}


function savePosts() {
    localStorage.setItem('posts', JSON.stringify(posts));
}

function loadPosts() {
    const savedPosts = JSON.parse(localStorage.getItem('posts')) || [];
    posts = savedPosts.map(post => ({
        ...post,
        liked: post.liked || false,
        clicks: post.clicks || 0
    }));
    updatePostsView();
}

document.addEventListener('DOMContentLoaded', function() {
    loadPosts(); // Load posts when the document is ready
    showTab('active'); // Show the active tab initially
    // Get the label element for the file input
    const fileUploadLabel = document.querySelector('.file-upload-label');

    // Add click event listener to the label
    fileUploadLabel.addEventListener('click', function() {
        // Trigger a click event on the file input element
        document.getElementById('photoUpload').click();
    });
});

function Posted() {
    location.reload(); 
    addPost();
}

function addPost() {
    const content = document.getElementById('newPostContent').value;
    const hint = document.getElementById('newPostHint').value;
    const languageSelect = document.getElementById('postLanguage');
    const language = languageSelect.options[languageSelect.selectedIndex].value;
    const postId = posts.length + 1; // Clculate next post ID based on the array length

    if (!content) {
        alert('Please enter some content to add a post.');
        return;
    } else{
        alert('Post Uploaded! GO to Home to Check!');
        }
    

    // Retrieve the images associated with this post from sessionStorage
    const uploadedPhotos = JSON.parse(sessionStorage.getItem('uploadedPhotos')) || {};
    const photos = uploadedPhotos[postId] || []; // Retrieve photos using the postId

    const newPost = {
        id: String(postId),
        content: content,
        hint: hint,
        language: language,
        photos: photos, // Attach the photos to the new post
        clicks: 0,
        attempts: 4,
        wrongAttempts: 0,
        timestamp: new Date(),
        status: 'active'
    };

    posts.push(newPost);
    savePosts();
    updatePostsView();
    document.getElementById('newPostContent').value = '';
    document.getElementById('newPostHint').value = '';
    // Clear the temporary storage for this post ID to prevent duplication
    delete uploadedPhotos[postId];
    sessionStorage.setItem('uploadedPhotos', JSON.stringify(uploadedPhotos));

}


function createPostHTML(post, elapsedTime) {
    let photosHtml = '';
    if (post.photos && post.photos.length) {
        photosHtml = `<div class="post-photos swiper-container" id="swiper_${post.id}" onclick="viewPost('${post.id}'); event.stopPropagation();">
                        <div class="swiper-wrapper">`;
        post.photos.forEach(photoUrl => {
            photosHtml += `<div class="swiper-slide"><img src="${photoUrl}" alt="Uploaded Photo" style="cursor: pointer;"></div>`;
        });
        photosHtml += `   </div>
                        <div class="swiper-button-prev"></div>
                        <div class="swiper-button-next"></div>
                      </div>`;
    }

    return `
<div class="post-container" id="post_${post.id}">
    ${photosHtml}
    <div class="user-photo">
        <img src="${post.photoUrl || 'default-photo.png'}" alt="User Photo" />
    </div>
    <h3 class="hint">${post.hint}</h3>
    <div class="input-group">
        <input type="text" id="input_${post.id}" class="form-control" placeholder="Enter content here" 
            ${post.attempts === 0 ? 'disabled' : ''} 
            style="border-color: ${post.attempts === 0 ? 'red' : 'initial'};">
        <div class="input-group-append">
            <button id="checkButton_${post.id}" class="btn btn-outline-secondary" 
                onclick="checkInput('${post.id}'); event.stopPropagation();">Check</button>
        </div>
    </div>
    <div class="like-container">
        <button id="likeButton_${post.id}" class="like-button" onclick="toggleLike('${post.id}'); event.stopPropagation();">
            &#10084; ${post.clicks}
        </button>
        <div class="wrong-attempts" style="color: red; font-weight: bold;">
            <span id="wrongAttempts_${post.id}">${post.wrongAttempts}</span>
        </div>
    </div>
    <button class="dropdown-button" onclick="toggleDropdown('${post.id}'); event.stopPropagation();">
        📝
    </button>
    <span class="time-posted">${elapsedTime}</span>
    <div id="dropdown_${post.id}" class="dropdown-content" style="display: none;">
        <p>${post.content} (${post.language}) - <small>${elapsedTime}</small></p>
        <span id="clicks_${post.id}">Clicks: ${post.clicks}</span>
        <a class="dropdown-item" href="#" onclick="editPost('${post.id}'); event.stopPropagation();">Edit</a>
        <a class="dropdown-item" href="#" onclick="deletePost('${post.id}'); event.stopPropagation();">Delete</a>
        <a class="dropdown-item" href="#" onclick="incrementClickCount('${post.id}'); event.stopPropagation();">Increment Click Count</a>
        <a class="dropdown-item" href="#" onclick="inputChecking('${post.id}'); event.stopPropagation();">Input Checking</a>
    </div>
</div>`;
}



function uploadPhotos(event) {
    const postId = posts.length + 1; // Predicting the new post's ID based on existing posts
    const files = Array.from(event.target.files);
    if (files.length > 6) {
        alert('You can upload a maximum of 6 photos.');
        return;
    }

    const photoPromises = files.map(file => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = () => reject('Failed to read file.');
            reader.readAsDataURL(file);
        });
    });

    Promise.all(photoPromises).then(images => {
        // Store the images temporarily, keyed by the post ID
        let uploadedPhotos = JSON.parse(sessionStorage.getItem('uploadedPhotos')) || {};
        uploadedPhotos[postId] = images; // Store images array under the corresponding postId
        sessionStorage.setItem('uploadedPhotos', JSON.stringify(uploadedPhotos));
    }).catch(error => {
        alert(error);
    });
}

function viewPost(postId) {
    // In a real application, this would navigate to a URL serving the post's content
    window.location.href = `/posts/${postId}.html`; // This assumes you have a routing setup to handle this URL
}

document.getElementById('photoUpload').addEventListener('change', function(event) {
    const files = Array.from(event.target.files);
    const photoContainer = document.getElementById('sortablePhotoList');
    photoContainer.innerHTML = ''; // Clear existing thumbnails if any

    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const li = document.createElement('li');
            li.style = 'margin: 5px; padding: 5px; float: left; list-style-type: none;';
            li.innerHTML = `<img src="${e.target.result}" style="width: 100px; height: auto; cursor: grab;">`;
            li.setAttribute('draggable', 'true');
            li.setAttribute('data-index', index);
            photoContainer.appendChild(li);
        };
        reader.readAsDataURL(file);
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const sortableList = document.getElementById('sortablePhotoList');

    let draggedItem = null;

    sortableList.addEventListener('dragstart', function(e) {
        draggedItem = e.target;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', draggedItem);
    }, false);

    sortableList.addEventListener('dragover', function(e) {
        e.preventDefault(); // Necessary to allow dropping
        e.dataTransfer.dropEffect = 'move';
        return false;
    }, false);

    sortableList.addEventListener('drop', function(e) {
        if (e.target.tagName === 'LI' && draggedItem !== e.target) {
            const listItems = Array.from(sortableList.children);
            const targetIndex = listItems.indexOf(e.target);
            sortableList.insertBefore(draggedItem, listItems[targetIndex]);
        }
        e.preventDefault(); // Prevent default to allow drop
    }, false);

    sortableList.addEventListener('dragend', function(e) {
        e.preventDefault();
        draggedItem = null;
    }, false);
});

document.addEventListener('DOMContentLoaded', function() {
    // Existing initialization code

    // Initialize all Swiper instances after posts are loaded
    posts.forEach(post => {
        if (post.photos && post.photos.length) {
            new Swiper('#swiper_' + post.id, {
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                loop: true,
            });
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    loadPosts(); // Load posts when the document is ready
    showTab('active'); // Show the active tab initially
});

// Add event listeners to customize swipe buttons behavior and styling
document.addEventListener('DOMContentLoaded', function() {
    const swiperButtons = document.querySelectorAll('.swiper-button-prev, .swiper-button-next');

    swiperButtons.forEach(button => {
        const arrow = button.querySelector('svg');

        // Prevent the default behavior (toggling dropdown menu) when swipe buttons are clicked
        button.addEventListener('click', function(event) {
            event.stopPropagation();
        });

        // Apply custom styling to the arrows
        button.addEventListener('mousedown', function() {
            arrow.style.setProperty('fill', 'darkgreen', 'important');
        });

        button.addEventListener('mouseup', function() {
            arrow.style.setProperty('fill', 'lightgray', 'important');
        });

        button.addEventListener('mouseleave', function() {
            arrow.style.setProperty('fill', 'lightgray', 'important');
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Load posts when the document is ready
    loadPosts();
    showTab('active');

    // Add event listeners to each input for checking with the Enter key
    document.querySelectorAll('.input-group input').forEach(input => {
        input.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                const postId = this.id.split('_')[1];
                checkInput(postId);
                event.preventDefault();  // Prevent the default action to stop form submission
            }
        });
    });
});

// Handle login form submission
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('loginForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent form submission

        var formData = new FormData(this);

        fetch('/login', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                window.location.href = '/';
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});


// Logout User
function logout() {
    fetch('/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

