import styled from 'styled-components';

const _Image = styled.img`
  display: inline-block;
  aspect-ratio: 16 / 9;
  width: 100%;
`;

export const HeroImage: React.FC = () => {
  return <_Image alt="Cyber TOON" src="./assets/heroImage.png" loading="eager" />;
};
