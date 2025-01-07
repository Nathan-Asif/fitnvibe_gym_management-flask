document.addEventListener("DOMContentLoaded", () => {
    console.log("Countup: " + typeof CountUp);

    const elements = document.querySelectorAll(".transition-image, .transition-button");

    const observerOptions = {
        threshold: 0.2,
    };

    const revealOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("show");
                observer.unobserve(entry.target);
            }
        });
    };

    const observer = new IntersectionObserver(revealOnScroll, observerOptions);

    elements.forEach(el => observer.observe(el));

    // Active Nav
    var currentPath = window.location.pathname;

    var navLinks = document.querySelectorAll('header .nav-link');

    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });

    // Sticky Header
    const header = document.querySelector("header");
    const stickyScrollSection = document.querySelector(".sticky_scroll");

    if (!stickyScrollSection) {
        console.error("Sticky scroll section not found.");
        return;
    }

    const sectionOffset = stickyScrollSection.getBoundingClientRect().top + window.scrollY;
    const triggerOffset = sectionOffset + stickyScrollSection.offsetHeight / 8 - window.innerHeight * 0.2; 

    const handleScroll = () => {
        if (window.scrollY >= triggerOffset) {
            if (!header.classList.contains("sticky")) {
                header.classList.add("sticky");
            }
        } else {
            if (header.classList.contains("sticky")) {
                header.classList.remove("sticky");
            }
        }
    };

    window.addEventListener("scroll", handleScroll);

    const toTopButton = document.getElementById("toTopButton");

    const handleScroll2 = () => {
        if (window.scrollY > 300) {
            toTopButton.classList.add("show");
            toTopButton.classList.remove("hide");
        } else {
            toTopButton.classList.add("hide");
            toTopButton.classList.remove("show");
        }
    };

    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    };

    window.addEventListener("scroll", handleScroll2);

    toTopButton.addEventListener("click", scrollToTop);
});

document.addEventListener('DOMContentLoaded', () => {
    const section = document.querySelector('.detail_sec');

    if (section) {
        const observer = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        document.querySelectorAll('.timer').forEach(timer => {
                            const targetValue = parseFloat(timer.getAttribute('data-to'));
                            const duration = 1000;
                            const refreshInterval = 100;
                            const formatter = (value) => value.toLocaleString();

                            let currentValue = 0;
                            const steps = Math.ceil(duration / refreshInterval);
                            const increment = targetValue / steps;

                            const updateCounter = () => {
                                currentValue += increment;
                                if (currentValue >= targetValue) {
                                    currentValue = targetValue;
                                    clearInterval(interval);
                                }
                                timer.textContent = formatter(currentValue);
                            };

                            const interval = setInterval(updateCounter, refreshInterval);
                        });

                        observer.unobserve(section);
                    }
                });
            },
            {
                threshold: 0.5
            }
        );

        observer.observe(section);
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // Check if it's the user's first visit
    // if (!localStorage.getItem('hasSeenModal')) {
        // If not, show the modal
        var myModal = new bootstrap.Modal(document.getElementById('myModal'));
        myModal.show();

        // Set flag in localStorage to remember that the user has seen the modal
        // localStorage.setItem('hasSeenModal', 'true');
    // }

    // Optionally handle button click to redirect user to the membership plans section or show plans
    document.querySelector('.custom-cta-btn').addEventListener('click', function () {
        // Close the modal
        var myModalInstance = bootstrap.Modal.getInstance(document.getElementById('myModal'));
        myModalInstance.hide();

        // Scroll to the membership section (assuming it's an anchor link on your page)
        document.getElementById('membershipPlansSection').scrollIntoView({ behavior: 'smooth' });
    });
});

