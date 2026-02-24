import React from 'react';
import Hero from '../components/Hero';
import WhyNutriLens from '../components/WhyNutriLens';
import QuestionCard from '../components/QuestionCard';
import UseCases from '../components/UseCases';
import FeaturesGrid from '../components/FeaturesGrid';

const Home = () => {
    return (
        <>
            <Hero />
            <WhyNutriLens />
            <QuestionCard />
            <UseCases />
            <FeaturesGrid />
        </>
    );
};

export default Home;
