import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

const ScrollToTop = () => {
    const { pathname, hash } = useLocation();

    useEffect(() => {
        // If there is no hash in the URL, scroll smoothly to the top of the page on route change.
        if (!hash) {
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'instant'
            });
        }
    }, [pathname, hash]);

    return null;
};

export default ScrollToTop;
