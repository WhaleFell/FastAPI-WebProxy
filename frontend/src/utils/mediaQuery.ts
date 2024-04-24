import { Ref, ref } from "vue";


export const useBreakPoint = (): Ref<string> => {

    const mediaType: Ref<string> = ref("")

    interface breakpoint {
        [key: string]: string;
    }

    // tailwindcss breakpoints
    // https://tailwindcss.com/docs/responsive-design
    let breakpoints: breakpoint = {
        '(min-width: 0px) and (max-width: 640px)': 'ssm',
        '(min-width: 640px) and (max-width: 768px)': 'sm',
        '(min-width: 768px) and (max-width: 1024px)': 'md',
        '(min-width: 1024px) and (max-width: 1280px)': 'lg',
        '(min-width: 1280px) and (max-width: 1536px)': 'xl',
        '(min-width: 1536px)': 'xxl',
    }

    const loopMatch = () => {
        for (let media in breakpoints) {
            if (window.matchMedia(media).matches) {
                console.log(breakpoints[media]);
                mediaType.value = breakpoints[media];
            }
        }
    }
    loopMatch();

    window.addEventListener('resize', loopMatch);

    return mediaType;

}

export const mediaType = useBreakPoint();